from .utils import ImportMixinUtils
from .raw import ImportMixinRaw
from .insert import ImportMixinInsert
from .process import ImportMixinProcess
from gn_modulator import SchemaMethods


class ImportMixinRelation(ImportMixinInsert, ImportMixinProcess, ImportMixinRaw, ImportMixinUtils):
    def process_relations(self):
        from_table = self.tables.get("mapping") or self.tables["data"]
        sm = SchemaMethods(self.schema_code)

        columns = SchemaMethods.get_table_columns(from_table)

        for index, key in enumerate(columns):
            if not sm.is_relationship(key):
                continue
            property = sm.property(key)

            # on commence par les n-n
            if property.get("relation_type") in ("n-n"):
                self.import_relation_n_n(from_table, key)

    def import_relation_n_n(self, from_table, key):
        sm = SchemaMethods(self.schema_code)

        self.sql[key] = {}

        property = sm.property(key)
        cor_table = property["schema_dot_table"]
        rel = SchemaMethods(property["schema_code"])

        raw_delete_view = self.table_name("raw_delete", key)
        process_delete_view = self.table_name("process_delete", key)
        raw_import_view = self.table_name("raw", key)
        process_import_view = self.table_name("process", key)

        # 0) clean

        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {process_delete_view}")
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {raw_delete_view}")
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {process_import_view}")
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {raw_import_view}")

        # 1) create raw_temp_table for n-n
        self.sql[key]["raw_view"] = self.sql_raw_view(
            from_table, raw_import_view, keys=[key], key_unnest=key
        )
        try:
            SchemaMethods.c_sql_exec_txt(self.sql[key]["raw_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_RAW_VIEW",
                msg=f"Erreur dans la creation de la vue 'raw' pour {key}: {str(e)}",
            )
            return

        self.sql[key]["process_view"] = self.sql_process_view(
            raw_import_view, process_import_view, keys=[key]
        )
        try:
            SchemaMethods.c_sql_exec_txt(self.sql[key]["process_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_PROCESS_VIEW",
                msg=f"Erreur dans la creation de la vue 'process' pour {key}: {str(e)}",
                key=key,
            )
            return

        # 3) insert / update / delete ??

        # - delete : tout depuis import_table
        # create_view for delete
        self.sql[key]["raw_delete_view"] = self.sql_raw_view(
            from_table, raw_delete_view, keys=[key], key_unnest=key
        )
        try:
            SchemaMethods.c_sql_exec_txt(self.sql[key]["raw_delete_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_RAW_VIEW",
                msg=f"Erreur dans la creation de la vue 'delete_raw' pour {key}: {str(e)}",
            )
            return

        self.sql[key]["process_delete_view"] = self.sql_process_view(
            raw_delete_view, process_delete_view, keys=[key]
        )
        try:
            SchemaMethods.c_sql_exec_txt(self.sql[key]["process_delete_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_PROCESS_DELETE_VIEW",
                msg=f"Erreur dans la creation de la vue 'delete_process' pour {key}: {str(e)}",
            )
            return

        self.sql[key][
            "delete"
        ] = f"""
DELETE FROM {cor_table} t
    USING {process_delete_view} j
    WHERE t.{sm.pk_field_name()} = j.{sm.pk_field_name()};
"""
        try:
            SchemaMethods.c_sql_exec_txt(self.sql[key]["delete"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_DELETE",
                msg=f"Erreur dans la suppression pour la relation {key}: {str(e)}",
            )
            return

        # - insert
        self.sql[key]["insert"] = self.sql_insert(
            process_import_view,
            keys=[sm.pk_field_name(), rel.pk_field_name()],
            dest_table=cor_table,
        )
        try:
            SchemaMethods.c_sql_exec_txt(self.sql[key]["insert"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_INSERT",
                msg=f"Erreur dans l'insertion pour la relation {key}: {str(e)}",
            )
            return
