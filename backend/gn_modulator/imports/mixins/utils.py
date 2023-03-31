import json
from pathlib import Path

from gn_modulator.schema import SchemaMethods
from gn_modulator.utils.env import schema_import
from gn_modulator import ModuleMethods


class ImportMixinUtils:
    sql_type_dict = {
        "integer": "INTEGER",
        "boolean": "BOOLEAN",
        "number": "FLOAT",
        "string": "VARCHAR",
        "date": "DATE",
        "datetime": "TIMESTAMP",
        "uuid": "UUID",
        "geometry": "GEOMETRY",
        "json": "JSONB",
    }

    def init_import(self):
        self.schema_code = self.schema_code or ModuleMethods.schema_code(
            self.module_code, self.object_code
        )
        if not self.schema_code:
            self.add_error(
                {
                    "code": "ERR_IMPORT_SCHEMA_CODE_NOT_FOND",
                    "msg": f"Il n'y a pas de schema pour module_code={self.module_code}, object_code={self.object_code}",
                }
            )
        SchemaMethods.c_sql_exec_txt(f"CREATE SCHEMA IF NOT EXISTS {schema_import}")

        # check srid (avoid sql injection)
        if self.options.get('srid'):
            try:
                int(self.options.get('srid'))
            except ValueError:
                self.add_error(
                    {
                        "code": "ERR_IMPORT_OPTIONS",
                        "msg": f"Le srid n'est pas valide {self.options.get('srid')}",
                    }
                )

    def pretty_infos(self):
        txt = ""
        if self.res.get("nb_data") is not None:
            txt += f"\n-- import csv file {Path(self.data_file_path).name}"
            txt += f"   {self.res.get('nb_data')} lignes\n\n"
        txt += f"   - {self.schema_code}\n"
        if self.res.get("nb_raw") != self.res.get("nb_process"):
            txt += f"       raw       : {self.res.get('nb_raw'):10d}\n"
        if self.res.get("nb_process"):
            txt += f"       process   : {self.res.get('nb_process'):10d}\n"
        if self.res.get("nb_insert"):
            txt += f"       insert    : {self.res['nb_insert']:10d}\n"
        if self.res.get("nb_update"):
            txt += f"       update    : {self.res['nb_update']:10d}\n"
        if self.res.get("nb_unchanged"):
            txt += f"       unchanged : {self.res['nb_unchanged']:10d}\n"

        return txt

    def count_and_check_table(self, table_type, table_name):
        if self.errors:
            return

        try:
            self.res[f"nb_{table_type}"] = SchemaMethods.c_sql_exec_txt(
                f"SELECT COUNT(*) FROM {table_name}"
            ).scalar()

        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_COUNT_VIEW",
                msg=f"Erreur avec la table/vue '{table_type}' {table_name}: {str(e)}",
            )
            return

        if self.res[f"nb_{table_type}"] == 0:
            self.add_error(
                code="ERR_IMPORT_COUNT_VIEW",
                msg=f"Erreur avec la table/vue '{table_type}' {table_name}: il n'y a n'a pas de données",
            )

    def table_name(self, type, key=None):
        """
        nom de la table
        """

        if type == "data":
            return f"{schema_import}.t_{self.id_import}_{type}"
        else:
            rel = f"_{key}" if key is not None else ""
            return f"{schema_import}.v_{self.id_import}_{type}_{self.schema_code.replace('.', '_')}{rel}"

    def add_error(self, code=None, msg=None, key=None, lines=None, values=None):
        self.errors.append(
            {"code": code, "msg": msg, "key": key, "lines": lines, "values": values}
        )
        self.status = "ERROR"

    def get_table_columns(self, table_name):
        if not self._columns.get(table_name):
            self._columns[table_name] = SchemaMethods.get_table_columns(table_name)
        return self._columns[table_name]

    def id_digitiser_key(self):
        for key in ["id_digitiser", "id_digitizer"]:
            if SchemaMethods(self.schema_code).has_property(key):
                return key
