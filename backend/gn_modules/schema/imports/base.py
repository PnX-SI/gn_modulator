"""
    SchemaData methode pour gerer les données depuis des fichiers .yml
    par exemple la nomenclature
"""

import copy
from pathlib import Path
import jsonschema
import marshmallow
from sqlalchemy.orm.exc import NoResultFound
from .. import errors
from gn_modules.utils.cache import get_global_cache, clear_global_cache, set_global_cache


class SchemaBaseImports:
    @classmethod
    def process_features(cls, data_name):
        """ """

        data = get_global_cache(["data", data_name, "definition"])

        if data is None:
            raise (Exception(f"La données demandée {data_name} n'existe pas"))

        data_file_path = get_global_cache(["data", data_name, "file_path"])

        infos = []

        for data_item in data["items"]:
            info = cls.process_data_item(data_item, data_file_path)

            infos.append(
                {
                    "file_path": str(data_file_path),
                    "schema_name": data_item["schema_name"],
                    "updates": info["updates"],
                    "errors": info["errors"],
                    "inserts": info["inserts"],
                    "items": cls.get_data_item(data_item, file_path=data_file_path),
                }
            )

        return infos

    def get_foreign_key(self, key_process, rel_test_values, process_one=False):

        sm_rel = self.cls(self.property(key_process)["schema_name"])
        if isinstance(rel_test_values, dict):
            sm_rel.get_foreign_keys(rel_test_values)
            return rel_test_values

        if self.property(key_process).get("relation_type") in ["1-n", "n-n"] and not process_one:
            fks = [
                self.get_foreign_key(key_process, value, process_one=True)
                for value in rel_test_values
            ]
            return [fk if isinstance(fk, dict) else {sm_rel.pk_field_name(): fk} for fk in fks]

        if not isinstance(rel_test_values, list):
            rel_test_values = [rel_test_values]

        rel_test_keys = sm_rel.attr("meta.unique")

        # on récupère le type de nomenclature au besoin
        if sm_rel.schema_name() == "ref_nom.nomenclature" and len(rel_test_values) == 1:
            rel_test_values.insert(0, self.property(key_process)["nomenclature_type"])

        d = {key: rel_test_values[index] for index, key in enumerate(rel_test_keys)}
        sm_rel.get_foreign_keys(d)
        rel_test_values = [d[key] for key in d]

        cache_key = "__".join([self.schema_name()] + list(map(lambda x: str(x), rel_test_values)))

        if cache_value := get_global_cache(["import_pk_keys", self.schema_name(), cache_key]):
            return cache_value

        if None in rel_test_values:
            return None

        try:
            m = sm_rel.get_row(
                rel_test_values,
                rel_test_keys,
                params={},  # sinon bug et utilise un param précédent ????
            ).one()
            pk = getattr(m, sm_rel.pk_field_name())
            set_global_cache(["import_pk_keys", self.schema_name(), cache_key], pk)
            return pk
        except NoResultFound:
            raise errors.SchemaImportPKError(
                "{}={} Pk not found {}".format(key_process, rel_test_values, sm_rel.schema_name())
            )

    def get_foreign_keys(self, d):

        for key in d:
            if not (
                (key in self.column_keys() and self.column(key).get("foreign_key"))
                or (key in self.relationship_keys())
            ):
                continue

            d[key] = self.get_foreign_key(key, d[key])

    def copy_keys(self, d):
        for key, keys in self.attr("meta.import.copy", {}).items():
            for k in keys:
                d[k] = d.get(k, d[key])

    def process_geoms(self, d):
        # boucle sur les valeur de d associées  à une geometrie
        for key in filter(lambda key: self.property(key)["type"] == "geometry", d):
            pass
            # d[key] = {
            # "type": self.column(key)['geometry_type'],
            # "coordinates": d[key]
            # }

    def pre_process_data(self, d):
        self.get_foreign_keys(d)
        self.copy_keys(d)
        self.process_geoms(d)

    def clean_data(self, d):

        for key in copy.copy(d):
            if key not in self.properties():
                if self.schema_name() == "schemas.utils.utilisateur.organisme":
                    print(self.schema_name(), "pop key", key)
                d.pop(key)

    @classmethod
    def get_data_items_from_file(cls, data_file):
        if data_file.suffix == ".yml":
            return cls.load_yml_file(data_file)
        else:
            raise errors.SchemaError("Le fichier {} n'est pas valide".format(data_file))

    @classmethod
    def get_data_item(cls, data_item, file_path):
        return (
            data_item["items"]
            if "items" in data_item
            else cls.get_data_items_from_file(Path(file_path).parent / data_item["file"])
            if "file" in data_item
            else []
        )

    @classmethod
    def process_data_item(cls, data_item, file_path):

        clear_global_cache(["import_pk_keys"])
        schema_name = data_item["schema_name"]
        sm = cls(schema_name)
        v_updates = []
        v_inserts = []
        v_errors = []

        test_keys = sm.attr("meta.unique")

        items = cls.get_data_item(data_item, file_path)

        i = 0
        for d in items:
            i = i + 1
            # validate_data
            try:

                # pre traitement
                values = [d.get(key) for key in test_keys]
                value = ", ".join([str(value) for value in values])

                sm.pre_process_data(d)

                # clean data
                sm.clean_data(d)

                values = [d.get(key) for key in test_keys]

                # pour visualiser quel ligne est insérée / modifiée
                value = ", ".join([str(value) for value in values])
                m = None

                # on tente un update
                try:
                    m, b_update = sm.update_row(values, d, test_keys, params={})
                    if b_update:
                        v_updates.append(value)

                # si erreur NoResultFound -> on tente un insert
                except NoResultFound:
                    sm.insert_row(d)
                    v_inserts.append(value)

            # erreur de validation des données
            except jsonschema.exceptions.ValidationError as e:
                msg_error = "{values} : {key}={quote}{value}{quote} ({msg}) (json schema)".format(
                    values=", ".join(values),
                    key=".".join(e.path),
                    value=e.instance,
                    quote="'" if isinstance(e.instance, str) else "",
                    msg=e.message,
                )
                v_errors.append({"value": value, "data": d, "error": msg_error})

            except marshmallow.exceptions.ValidationError as e:
                key = list(e.messages.keys())[0]
                msg_error = (
                    "{values} : {key}={quote}{value}{quote} ({msg}) (marshmallow schema)".format(
                        values=", ".join(values),
                        key=key,
                        quote="'" if isinstance(e.data[key], str) else "",
                        value=e.data[key],
                        msg=", ".join(e.messages[key]),
                    )
                )
                v_errors.append({"value": value, "data": d, "error": msg_error})

            except errors.SchemaImportPKError as e:
                msg_error = "{values}: {err}".format(
                    values=", ".join(map(lambda x: str(x), values)), err=str(e)
                )
                v_errors.append({"value": value, "data": d, "error": msg_error})

        return {"updates": v_updates, "inserts": v_inserts, "errors": v_errors}

    @classmethod
    def log_data_info_detail(cls, info, info_type, details=False):
        """
        affichage du detail pour insert ou update
        un peu compliqué
        """
        items = info[info_type]
        nb = len(items)

        if items and type(items[0]) is list:
            list_first_key = list(dict.fromkeys([elem[0] for elem in items]))
            items_new = []
            for elem_first_key in list_first_key:
                list_second_key = [
                    elem[1] for elem in filter(lambda e: e[0] == elem_first_key, items)
                ]
                elem_new = "{}.({})".format(elem_first_key, ", ".join(list_second_key))
                items_new.append(elem_new)
            items = items_new

        # detail = '\n  - {}  ({})'.format(info_type, nb)
        detail = ""

        if nb and details:
            tab = "      - "
            detail += "{}{}".format(tab, ("\n" + tab).join(items))
            detail += "\n"
        return detail

        # return '\n    - '.join(['' + '.'.join(elem) if type(elem) is list else elem for elem in info[info_type]])

    @classmethod
    def txt_data_info(cls, info, details=False):
        """ """

        txt = ""
        # detail_updates = cls.log_data_info_detail(info, "updates", details=details)
        # detail_inserts = cls.log_data_info_detail(info, "inserts", details=details)
        # detail_errors = cls.log_data_info_detail(info, "errors", details=details)
        # print('detail_errors', detail_errors)
        # print('detail_errors', info['errors'])
        # txt += '  - {schema_name}\n'.format(schema_name=info['schema_name'])
        # txt += '    - items ({})\n'.format(len(info['items']))
        # txt += '    - updates ({})\n'.format(len(info['updates']))
        # txt += '{}'.format(detail_updates)
        # txt += '    - inserts ({})\n'.format(len(info['inserts']))
        # txt += '{}'.format(detail_inserts)

        txt = """    - {schema_name:45}    #:{nb_items:4}    I:{nb_inserts:4}    U:{nb_updates:4}    E:{nb_errors:4}""".format(
            schema_name=info["schema_name"],
            nb_items=len(info["items"]),
            nb_inserts=len(info["inserts"]),
            nb_updates=len(info["updates"]),
            nb_errors=len(info["errors"]),
        )

        for info_error in info["errors"]:
            txt += "\n      - {}".format(info_error["error"])

        return txt

    @classmethod
    def txt_data_infos(cls, infos_file, details=False):
        """ """

        txt_list = []
        for schema_name, info_file_value in infos_file.items():
            # txt = "  - {}".format(schema_name, len(info_file_value))
            txt = "  - {}".format(schema_name)
            for info in info_file_value:
                txt += "\n{}".format(cls.txt_data_info(info, details=details))
            txt_list.append(txt)
        return "\n\n".join(txt_list)
