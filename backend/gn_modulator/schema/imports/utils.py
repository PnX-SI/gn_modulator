from pathlib import Path
import math, random
from geonature.utils.env import db
from utils_flask_sqla.generic import GenericTable
from gn_modulator.utils.env import schema_import
from gn_modulator.utils.cache import set_global_cache, get_global_cache


class SchemaUtilsImports:
    """
    methodes pour aider aux imports
    """

    @classmethod
    def count_and_check_table(cls, import_number, schema_code, dest_table, table_type):
        try:
            nb_lines = cls.c_sql_exec_txt(f"SELECT COUNT(*) FROM {dest_table}").scalar()
            cls.import_set_infos(import_number, schema_code, f"nb_{table_type}", nb_lines)
        except Exception as e:
            cls.import_add_error(
                import_number,
                schema_code,
                code="ERR_IMPORT_COUNT_VIEW",
                msg=f"Erreur avec la table/vue '{table_type}' {dest_table}: {str(e)}",
            )
            return

        if nb_lines == 0:
            cls.import_add_error(
                import_number,
                schema_code,
                code="ERR_IMPORT_COUNT_VIEW",
                msg=f"Erreur avec la table/vue '{table_type}' {dest_table}: il n'y a n'a pas de données",
            )

    @classmethod
    def generate_import_number(cls):
        """
        genere un nombre aleatoire pour différer tous les imports
        TODO utiliser un serial ?
        """
        return math.floor(random.random() * 1e6)

    @classmethod
    def import_pretty_infos(cls, import_number, schema_code):
        """
        met en forme les resultats de l'import
        """

        import_infos = cls.import_get_infos(import_number, schema_code)
        txt = ""
        txt += f"   - {schema_code}\n"
        txt += f"       raw       : {import_infos['nb_raw']:10d}\n"
        if import_infos["nb_raw"] != import_infos["nb_process"]:
            txt += f"       processed : {import_infos['nb_process']:10d}\n"
        if import_infos["nb_insert"]:
            txt += f"       insert    : {import_infos['nb_insert']:10d}\n"
        if import_infos["nb_update"]:
            txt += f"       update    : {import_infos['nb_update']:10d}\n"
        if import_infos["nb_unchanged"]:
            txt += f"       unchanged : {import_infos['nb_unchanged']:10d}\n"

        return txt

    @classmethod
    def import_clean_tables(cls, import_number, schema_code, keep_raw):
        """
        Drop import tables
        """
        tables = cls.import_get_infos(import_number, schema_code, "tables", required=True)

        if not keep_raw:
            cls.c_sql_exec_txt(f"DROP TABLE IF EXISTS {tables['import']} CASCADE")
        else:
            cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables['process']} CASCADE")
            cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables['preprocess']} CASCADE")
            cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables['raw']} CASCADE")

    @classmethod
    def import_table_name(cls, import_number, schema_code, data_file_path, type, key=None):
        """
        table dans laquelle on importe le fichier csv
        """

        if type == "import":
            return f"{schema_import}.t_{type}_{Path(data_file_path).stem.lower()}_{import_number}"
        else:
            rel = f"_{key}" if key is not None else ""
            return f"{schema_import}.v_{type}_{Path(data_file_path).stem.lower()}_{import_number}_{schema_code.replace('.', '_')}{rel}"

    @classmethod
    def import_init(cls, import_number, schema_code, data_file_path, pre_process_file_path):
        """
        create schema <schema_import> if not exists
        drop previous tables ??
        """
        cls.import_set_infos(import_number, schema_code, "data_file_path", data_file_path)
        cls.import_set_infos(
            import_number, schema_code, "pre_process_file_path", pre_process_file_path
        )
        cls.import_set_infos(import_number, schema_code, "errors", [])

        for table_type in ["import", "raw", "preprocess", "process"]:
            table_type2 = (
                "import"
                if (table_type == "preprocess" and not pre_process_file_path)
                else table_type
            )
            cls.import_set_infos(
                import_number,
                schema_code,
                f"tables.{table_type}",
                cls.import_table_name(import_number, schema_code, data_file_path, table_type2),
            )

        cls.c_sql_exec_txt(f"CREATE SCHEMA IF NOT EXISTS {schema_import}")

    @classmethod
    def import_get_infos(cls, import_number, schema_code, key=None, required=False):
        cache_keys = ["import_info", import_number, schema_code]
        if key is not None:
            cache_keys += key.split(".")
        res = get_global_cache(cache_keys)
        if required and res is None:
            raise cls.SchemaImportRequiredInfoNotFoundError(
                f"Required import_info not found for {{import_number: {import_number}, schema_code: {schema_code}, key: {key}}}"
            )
        return res

    @classmethod
    def import_set_infos(cls, import_number, schema_code, key, value):
        cache_keys = ["import_info", import_number, schema_code] + key.split(".")
        set_global_cache(cache_keys, value)

    @classmethod
    def import_add_error(cls, import_number, schema_code, code=None, msg=None):
        errors = cls.import_get_infos(import_number, schema_code, "errors")
        errors.append({"code": code, "msg": msg})
