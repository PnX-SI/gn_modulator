'''
    SchemaData methode pour gerer les données depuis des fichiers.json
    par exemple la nomenclature
'''

from calendar import c
import os
import copy
from pathlib import Path
from typing import Container
import jsonschema
import marshmallow
from pkg_resources import resource_exists
from sqlalchemy import schema, text
from sqlalchemy.orm.exc import NoResultFound
from geonature.utils.env import db
from utils_flask_sqla.generic import GenericTable

from . import errors

class SchemaImports:

    @classmethod
    def load_and_validate_data(cls, data_file_path):
        '''
            - charge des données depuis un fichier json
            - recupère le schéma associé depuis schema_name
            - valide la donnée par raport au schema
            - retourne la données
        '''

        # lecture des fichiers data et schema

        # data_path = cls.data_path(data_name) / '{}.json'.format(data_name)
        # if data_path.is_dir():
        #     for root, dirs, files in os.walk(data_path, followlinks=True):
        #         for f in files:
        #             if f.endswith('.json'):
        #                 cls.load_and_validate_data

        data = cls.load_json_file(data_file_path)

        schema = cls.get_global_cache('reference', 'data')

        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            print(e)
            return

        return data

    @classmethod
    def data_file_sub_path(cls, data_file_path):
        return str(data_file_path).replace(str(cls.config_directory() / 'data') + '/', '')

    @classmethod
    def process_data(cls, data_file_path):
        '''
        '''

        data = cls.load_and_validate_data(data_file_path)
        infos = []

        for data_item in data:
            info = cls.process_data_item(data_item, data_file_path)

            infos.append({
                'file_path': str(data_file_path),
                'schema_name': data_item['schema_name'],
                'updates': info['updates'],
                'errors': info['errors'],
                'inserts': info['inserts'],
                'items': cls.get_data_item(data_item, file_path=data_file_path),
            })

        return infos

    def get_foreign_key(self, key_process, rel_test_values, process_one=False):

        sm_rel = self.cls(self.property(key_process)['schema_name'])
        if isinstance(rel_test_values, dict):
            sm_rel.get_foreign_keys(rel_test_values)
            return rel_test_values

        if (
            self.property(key_process).get('relation_type') in ["1-n", "n-n"]
            and not process_one
        ):
            fks = [
                self.get_foreign_key(key_process, value, process_one=True)
                for value in rel_test_values
            ]
            return [
                fk if isinstance(fk, dict)
                else {
                    sm_rel.pk_field_name(): fk
                }
                for fk in fks
            ]

        if not isinstance(rel_test_values, list):
            rel_test_values = [rel_test_values]

        rel_test_keys = sm_rel.attr('meta.unique')

        # on récupère le type de nomenclature au besoin
        if (
            sm_rel.schema_name() == 'ref_nom.nomenclature'
            and len(rel_test_values) == 1
        ):
            rel_test_values.insert(0, self.property(key_process)['nomenclature_type'])

        d = {
            key: rel_test_values[index]
            for index, key in enumerate(rel_test_keys)
        }
        sm_rel.get_foreign_keys(d)
        rel_test_values = [d[key] for key in d]

        cache_key = '__'.join([self.schema_name()] + list(map(lambda x: str(x), rel_test_values)))

        if cache_value := self.cls.get_global_cache('import_pk_keys', cache_key):
            return cache_value

        if None in rel_test_values:
            return None

        try:
            m = sm_rel.get_row(rel_test_values, rel_test_keys)
            pk = getattr(m, sm_rel.pk_field_name())
            self.cls.set_global_cache('import_pk_keys', cache_key, pk)
            return pk
        except NoResultFound:
            raise errors.SchemaImportPKError(
                "{}={} Pk not found {}"
                .format(
                    key_process,
                    rel_test_values,
                    sm_rel.schema_name()
                )
            )
            return None

    def get_foreign_keys(self, d):

        for key in d:
            if not (
                (key in self.column_keys() and self.column(key).get('foreign_key'))
                or (key in self.relationship_keys())
            ):
                continue
            d[key] = self.get_foreign_key(key, d[key])

    def copy_keys(self, d):
        for key, keys in self.attr('meta.import.copy', {}).items():
            for k in keys:
                d[k] = d.get(k, d[key])

    def process_geoms(self, d):
        # boucle sur les valeur de d associées  à une geometrie
        for key in filter(
            lambda key: self.property(key)['type'] == 'geometry',
            d
        ):
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
                if self.schema_name() == 'schemas.utils.utilisateur.organisme':
                    print(self.schema_name(), 'pop key', key)
                d.pop(key)

    @classmethod
    def get_data_items_from_file(cls, data_file):
        if data_file.suffix == '.json':
            return cls.load_json_file(data_file)
        else:
            raise errors.SchemaError(
                "Le fichier {} n'est pas valide"
                .format(data_file)
            )

    @classmethod
    def get_data_item(cls, data_item, file_path):
        return (
            data_item['items'] if 'items' in data_item
            else cls.get_data_items_from_file(Path(file_path).parent / data_item['file']) if 'file' in data_item
            else []
        )

    @classmethod
    def process_data_item(cls, data_item, file_path):

        cls.clear_global_cache('import_pk_keys')
        schema_name = data_item['schema_name']
        sm = cls(schema_name)

        v_updates = []
        v_inserts = []
        v_errors = []

        test_keys = sm.attr('meta.unique')

        items = cls.get_data_item(data_item, file_path)

        i = 0
        for d in items:
            i = i + 1
            # validate_data
            try:

                # pre traitement
                values = [d.get(key) for key in test_keys]
                value = ', '.join([str(value) for value in values])

                sm.pre_process_data(d)

                # clean data
                sm.clean_data(d)

                # print('after pre process', d)
                values = [d.get(key) for key in test_keys]

                # pour visualiser quel ligne est insérée / modifiée
                value = ', '.join([str(value) for value in values])
                m = None

                # on tente un update
                try:
                    m, b_update = sm.update_row(
                        values,
                        d,
                        test_keys
                    )
                    if b_update:
                        v_updates.append(value)

                # si erreur NoResultFound -> on tente un insert
                except NoResultFound:
                    m = sm.insert_row(d)
                    v_inserts.append(value)

            # erreur de validation des données
            except jsonschema.exceptions.ValidationError as e:
                msg_error = (
                    '{values} : {key}={quote}{value}{quote} ({msg}) (j)'
                    .format(
                        values=', '.join(values),
                        key='.'.join(e.path),
                        value=e.instance,
                        quote="'" if isinstance(e.instance, str) else "",
                        msg=e.message
                    )
                )
                v_errors.append({"value": value, "data": d, "error": msg_error})

            except marshmallow.exceptions.ValidationError as e:
                print(e)
                key = list(e.messages.keys())[0]
                msg_error = (
                    '{values} : {key}={quote}{value}{quote} ({msg}) (m)'
                    .format(
                        values=', '.join(values),
                        key=key,
                        quote="'" if isinstance(e.data[key], str) else "",
                        value=e.data[key],
                        msg=', '.join(e.messages[key])
                    )
                )
                v_errors.append({"value": value, "data": d, "error": msg_error})

            except errors.SchemaImportPKError as e:
                msg_error = (
                    '{values}: {err}'
                    .format(
                        values=', '.join(values),
                        err=str(e)
                    )
                )
                v_errors.append({"value": value, "data": d, "error": msg_error})

        return {'updates': v_updates, 'inserts': v_inserts, 'errors': v_errors}

    @classmethod
    def log_data_info_detail(cls, info, info_type, details=False):
        '''
            affichage du detail pour insert ou update
            un peu compliqué
        '''
        items = info[info_type]
        nb = len(items)

        if items and type(items[0]) is list:
            list_first_key = list(dict.fromkeys([elem[0] for elem in items]))
            items_new = []
            for elem_first_key in list_first_key:
                list_second_key = [elem[1] for elem in filter(lambda e: e[0] == elem_first_key, items)]
                elem_new = '{}.({})'.format(
                    elem_first_key,
                    ', '.join(list_second_key)
                )
                items_new.append(elem_new)
            items = items_new

        # detail = '\n  - {}  ({})'.format(info_type, nb)
        detail = ''

        if nb and details:
            tab = '      - '
            detail += '{}{}'.format(
                tab,
                ('\n' + tab).join(items)
            )
            detail += '\n'
        return detail

        # return '\n    - '.join(['' + '.'.join(elem) if type(elem) is list else elem for elem in info[info_type]])

    @classmethod
    def txt_data_info(cls, info, details=False):
        txt = ''
        detail_updates = cls.log_data_info_detail(info, 'updates', details=details)
        detail_inserts = cls.log_data_info_detail(info, 'inserts', details=details)
        detail_errors = cls.log_data_info_detail(info, 'errors', details=details)
        # print('detail_errors', detail_errors)
        # print('detail_errors', info['errors'])
        # txt += '  - {schema_name}\n'.format(schema_name=info['schema_name'])
        # txt += '    - items ({})\n'.format(len(info['items']))
        # txt += '    - updates ({})\n'.format(len(info['updates']))
        # txt += '{}'.format(detail_updates)
        # txt += '    - inserts ({})\n'.format(len(info['inserts']))
        # txt += '{}'.format(detail_inserts)

        txt = (
            '  - {schema_name:45}    #:{nb_items:4}    I:{nb_inserts:4}    U:{nb_updates:4}    E:{nb_errors:4}'
            .format(
                schema_name=info['schema_name'],
                nb_items=len(info['items']),
                nb_inserts=len(info['inserts']),
                nb_updates=len(info['updates']),
                nb_errors=len(info['errors'])
            )
        )

        for info_error in info['errors']:
            txt += '\n    - {}'.format(info_error['error'])

        return txt

    @classmethod
    def txt_data_infos(cls, infos_file, details=False):
        txt_list = []
        for schema_name, info_file_value in infos_file.items():
            txt = '- {}'.format(schema_name, len(info_file_value))
            for info in info_file_value:
                txt += '\n{}'.format(cls.txt_data_info(info, details=details))
            txt_list.append(txt)
        return '\n\n'.join(txt_list)

############################################
#
# Bulk import
#
############################################

    @classmethod
    def import_bulk_data(cls, schema_name, file_path):
        '''
            import de données
        '''

        temp_table = "public.tmp_import_bulk_data"

        #) 0) clean
        db.engine.execute(f"DROP VIEW IF EXISTS public.v_tmp_import_bulk_data CASCADE;")
        db.engine.execute(f"DROP VIEW IF EXISTS public.v_tmp_import_bulk_data_inter CASCADE;")
        db.engine.execute(f"DROP TABLE IF EXISTS public.tmp_import_bulk_data CASCADE;")

        # 1) csv -> table temporaire
        cls.csv_to_temp_table(temp_table, file_path)

        # 2) table temporaire -> vue d'import_1
        v_temp_table_1 = cls.temp_table_to_import_view_1(schema_name, temp_table)

        # 2.2) table temporaire -> vue d'import_2
        v_temp_table_2 = cls.temp_table_to_import_view_2(schema_name, v_temp_table_1)


        # 3) commande insert
        cls.import_view_to_insert(schema_name, v_temp_table_2)

        # 4) commande update
        cls.import_view_to_update(schema_name, v_temp_table_2)

        # 5) process relations
        # cls.process_import_relations(schema_name, temp_table)
        return "ok"


    # @classmethod
    # def process_import_relations(cls, schema_name, temp_table):
    #     sm = cls(schema_name)
    #     columns = (
    #         GenericTable(temp_table.split('.')[1], temp_table.split('.')[0], db.engine)
    #         .tableDef
    #         .columns
    #     )

    #     for index, column in enumerate(columns):
    #         if not sm.is_relationship(column.key):
    #             continue
    #         property = sm.property(column.key)

    #         if property.get('relation_type') in ('n-n'):
    #             rel = cls(property.get('schema_name'))
    #             print(key, rel)
    #             txt = f"""
    # CREATE VIEW test_import_{rel.schema_name()} AS
    # SELECT
    #     UNNEST({key}) as id_nomenclature,
    #     t.{sm.pk_field_name()}
    #     FROM {temp_table}
    #     JOIN {sm.sql_schema_dot_table()} t ON t.{pk_field_name}
    # """

    @classmethod
    def import_view_to_update(cls, schema_name, v_temp_table):

        sm = cls(schema_name)
        columns = (
            GenericTable(v_temp_table.split('.')[1], v_temp_table.split('.')[0], db.engine)
            .tableDef
            .columns
        )

        v_column_keys = map(
            lambda x: x.key,
            filter(
                lambda x: sm.has_property(x.key) and sm.is_column(x.key),
                columns
            ),
        )

        v_set_keys = map(
            lambda x: x.key,
            filter(
                lambda x: sm.has_property(x.key) and sm.is_column(x.key) and not sm.property(x.key).get('primary_key'),
                columns
            ),
        )

        txt_set_keys = ",\n    ".join(
            map(
                lambda x: f"{x}=a.{x}",
                v_set_keys
            )
        )
        txt_columns_keys = ",\n        ".join(v_column_keys)

        txt_update = f"""
UPDATE {sm.sql_schema_dot_table()} t SET
    {txt_set_keys}
FROM (
    SELECT
        {txt_columns_keys}
    FROM {v_temp_table}
)a
WHERE a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
;
"""

        print(txt_update)
        res = db.engine.execute(txt_update)


    @classmethod
    def import_view_to_insert(cls, schema_name, v_temp_table):

        sm = cls(schema_name)
        columns = (
            GenericTable(v_temp_table.split('.')[1], v_temp_table.split('.')[0], db.engine)
            .tableDef
            .columns
        )

        v_column_keys = map(
            lambda x: x.key,
            filter(
                lambda x: sm.has_property(x.key) and sm.is_column(x.key) and not sm.property(x.key).get('primary_key'),
                columns
            ),
        )

        txt_columns_keys = ",\n    ".join(v_column_keys)

        txt_insert=f"""
INSERT INTO {sm.sql_schema_dot_table()} (
    {txt_columns_keys}
)
SELECT
    {txt_columns_keys}
FROM {v_temp_table}
WHERE {sm.pk_field_name()} IS NULL
;
"""

        print(txt_insert)
        res = db.engine.execute(txt_insert)


    @classmethod
    def temp_table_to_import_view_1(cls, schema_name, temp_table):
        '''
            ajout de nomenclature type
        '''
        v_temp_table_1 = f"{temp_table.split('.')[0]}.v_{temp_table.split('.')[1]}_inter"

        columns = (
            GenericTable(temp_table.split('.')[1], temp_table.split('.')[0], db.engine)
            .tableDef
            .columns
        )

        sm = cls(schema_name)

        v_txt_columns = []

        # colonnes
        for index, column in enumerate(columns):
            txt_col = None
            if sm.has_property(column.key) and sm.is_column(column.key) and sm.property(column.key).get('nomenclature_type'):
                nomenclature_type = sm.property(column.key).get('nomenclature_type')
                v_txt_columns.append(f"""CASE
        WHEN t.{column.key} = '' THEN NULL
        WHEN t.{column.key} IS NOT NULL AND t.{column.key} NOT LIKE '%%|%%'
            THEN CONCAT('{nomenclature_type}','|',t.{column.key})
        ELSE NULL
    END AS {column.key}""")
                continue
            v_txt_columns.append(f"""CASE
        WHEN t.{column.key}::text = '' THEN NULL
        ELSE t.{column.key}
    END AS {column.key}""")

        txt_columns = ",\n    ".join(v_txt_columns)
        txt_from = f"FROM {temp_table} t"

        txt_view = f"""CREATE VIEW {v_temp_table_1} AS
SELECT
    {txt_columns}
{txt_from}
;"""

        print(txt_view)
        db.engine.execute(str(txt_view))

        return v_temp_table_1




    @classmethod
    def temp_table_to_import_view_2(cls, schema_name, v_temp_table_1):
        '''
            TODO eclater le code
            recursif sur les join ??
        '''

        v_temp_table_2 = f"{v_temp_table_1.replace('inter', '')}"

        columns = (
            GenericTable(v_temp_table_1.split('.')[1], v_temp_table_1.split('.')[0], db.engine)
            .tableDef
            .columns
        )
        sm = cls(schema_name)

        v_txt_columns = []

        # colonnes
        for index, column in enumerate(columns):
            txt_col = None

            # si cle non dans schema (par ex id_import)
            if not (sm.has_property(column.key)):
                v_txt_columns.append(f"t.{column.key}")
                continue

            property = sm.property(column.key)

            # si c'est la clé primaire
            if property.get('primary_key'):
                v_txt_columns.append(f"j_{index}.{column.key}")
                continue

            if property.get('foreign_key'):
                rel = cls(property.get('schema_name'))
                v_txt_columns.append(f"j_{index}.{rel.pk_field_name()} AS {column.key}")
                continue

            # boolean
            if property.get('type') == "boolean":
                v_txt_columns.append(f"""CASE WHEN t.{column.key} = 't' THEN TRUE WHEN t.{column.key} = 't' THEN FALSE ELSE NULL END AS {column.key}""")
                continue

            # number
            if property.get('type') in ("number", "date", "integer"):
                sql_type = "float" if property.get('type') =='number' else property.get('type')
                v_txt_columns.append(f"t.{column.key}::{sql_type}")
                continue

                # # integer
                # if property.get('type') == "integer":
                #     v_txt_columns.append(f"CASE WHEN t.{column.key} = '' THEN NULL ELSE t.{column.key}::float END AS {column.key}")
                #     continue

                # # integer
                # if property.get('type') == "date":
                #     v_txt_columns.append(f"t.{column.key}::date")
                #     continue

            # si geom
            if property.get('type') == "geometry":
                v_txt_columns.append(f"ST_SETSRID(ST_FORCE2D(ST_GEOMFROMEWKT(t.{column.key})), {property.get('srid')}) AS {column.key}")
                continue

            v_txt_columns.append(f"t.{column.key}")

        v_txt_joins = []
        for index, column in enumerate(columns):
            txt_join = None

            # si cle non dans schema
            if not (sm.has_property(column.key)):
                continue

            property = sm.property(column.key)
            # si c'est la clé primaire
            if property.get('primary_key'):

                join_on = " AND ".join(
                    map(
                        lambda x: f'j_{index}.{x} = t.{x}',
                        sm.attr('meta.unique')
                    )
                )
                v_txt_joins.append(
                    f"LEFT JOIN {sm.sql_schema_dot_table()} AS j_{index} ON {join_on}"
                )
                continue

            if property.get('foreign_key'):
                rel = cls(property.get('schema_name'))
                unique = rel.attr('meta.unique')
                cond_rel2 = ""
                for  index_unique, k_unique in enumerate(unique):
                    if rel.property(k_unique).get('foreign_key'):
                        rel2 = cls(rel.property(k_unique)['schema_name'])
                        rel2_pk_unique = rel2.attr('meta.unique')[0]

    #                     if property.get('nomenclature_type'):
    #                         v_txt_joins.append(
    #                             f"""LEFT JOIN {rel2.sql_schema_dot_table()} AS j_{index}_0
    # ON j_{index}_0.{rel2_pk_unique} = '{property['nomenclature_type']}'"""
    #                         )
    #                     else:
                        v_txt_joins.append(
                            f"""LEFT JOIN {rel2.sql_schema_dot_table()} AS j_{index}_0
    ON j_{index}_0.{rel2_pk_unique} = SPLIT_PART(t.{column.key}, '|', {index_unique + 1})"""
                        )
                        cond_rel2 = f" AND j_{index}_0.{rel2.pk_field_name()} = j_{index}.{k_unique}"
                    else:
    #                     if property.get('nomenclature_type'):
    #                         v_txt_joins.append(
    #                             f"""LEFT JOIN {rel.sql_schema_dot_table()} AS j_{index}
    # ON j_{index}.{k_unique} = CASE
    #     WHEN t.{column.key} LIKE '%,%' THEN SPLIT_PART(t.{column.key}, ',', {index_unique + 1})
    #     ELSE t.{column.key}
    #     END{cond_rel2}"""
    #                         )
                        # else:
                        v_txt_joins.append(
                            f"""LEFT JOIN {rel.sql_schema_dot_table()} AS j_{index}
    ON j_{index}.{k_unique} = SPLIT_PART(t.{column.key}, '|', {index_unique + 1}){cond_rel2}"""
                        )

                continue

        txt_columns = ",\n    ".join(v_txt_columns)
        txt_from = f"FROM {v_temp_table_1} t"
        txt_joins = "\n".join(v_txt_joins)

        txt_view = f"""
CREATE VIEW {v_temp_table_2} AS
SELECT
{txt_columns}
{txt_from}
{txt_joins}
;
"""

        print(txt_view)
        db.engine.execute(str(txt_view))

        return v_temp_table_2

    @classmethod
    def csv_to_temp_table(cls, temp_table, file_path):
        '''
            créé une table temporaire à partir d'un fichier csv
        '''

        with open(file_path, 'r') as f:
            line = f.readline()

            columns = line.replace('\n', '').split("\t")
            print(columns)
            columns_fields = ', '.join(columns)
            columns_sql = '\n'.join(map(lambda x: f'{x} VARCHAR,', columns))

            print('Create table')
            txt_create_temp_table = f"""
                CREATE TABLE IF NOT EXISTS {temp_table} (
                    id_import SERIAL NOT NULL,
                    {columns_sql}
                    CONSTRAINT pk_{'_'.join(temp_table.split('.'))}_id_import PRIMARY KEY (id_import)
                );
"""
            db.engine.execute(txt_create_temp_table)

            print(f'Copy data {columns_fields}')
            db.session.connection().connection.cursor().copy_expert(f"COPY {temp_table}({columns_fields}) FROM STDIN;", f)
            db.session.commit()
