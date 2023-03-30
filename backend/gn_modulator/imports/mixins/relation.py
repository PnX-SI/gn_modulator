from .utils import ImportMixinUtils
from .raw import ImportMixinRaw
from .insert import ImportMixinInsert
from .process import ImportMixinProcess
from gn_modulator import SchemaMethods


class ImportMixinRelation(ImportMixinInsert, ImportMixinProcess, ImportMixinRaw, ImportMixinUtils):
    def get_n_n_relations(self, from_table):
        sm = SchemaMethods(self.schema_code)
        return list(
            filter(
                lambda x: sm.is_relationship(x) and sm.property(x).get("relation_type") == "n-n",
                self.get_table_columns(from_table),
            )
        )

    def process_relations_view(self):
        from_table = self.tables.get("mapping") or self.tables["data"]

        for key in self.get_n_n_relations(from_table):
            self.process_relation_views(key, from_table)

    def process_relations_data(self):
        from_table = self.tables.get("mapping") or self.tables["data"]

        for key in self.get_n_n_relations(from_table):
            self.process_relation_data(key)

    def process_relation_views(self, key, from_table):
        self.sql["relations"] = self.sql.get("relations") or {}
        self.tables["relations"] = self.tables.get("relations") or {}
        sql = self.sql["relations"][key] = {}
        tables = self.tables["relations"][key] = {}

        tables["raw_delete_view"] = self.table_name("raw_delete", key)
        tables["process_delete_view"] = self.table_name("process_delete", key)
        tables["raw_view"] = self.table_name("raw", key)
        tables["process_view"] = self.table_name("process", key)

        # 0) clean
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables['process_delete_view']}")
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables['raw_delete_view']}")
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables['process_view']}")
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables['raw_view']}")

        sql["raw_view"] = self.sql_raw_view(
            from_table, tables["raw_view"], keys=[key], key_unnest=key
        )

        # 1) create raw_temp_table for n-n
        try:
            SchemaMethods.c_sql_exec_txt(sql["raw_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_RAW_VIEW",
                msg=f"Erreur dans la creation de la vue 'raw' pour {key}: {str(e)}",
            )
            return

        sql["process_view"] = self.sql_process_view(
            tables["raw_view"], tables["process_view"], keys=[key]
        )

        try:
            SchemaMethods.c_sql_exec_txt(sql["process_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_PROCESS_VIEW",
                msg=f"Erreur dans la creation de la vue 'process' pour {key}: {str(e)}",
                key=key,
            )
            return

        sql["raw_delete_view"] = self.sql_raw_view(
            from_table, tables["raw_delete_view"], keys=[key], key_unnest=key
        )
        try:
            SchemaMethods.c_sql_exec_txt(sql["raw_delete_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_RAW_VIEW",
                msg=f"Erreur dans la creation de la vue 'delete_raw' pour {key}: {str(e)}",
            )
            return

        sql["process_delete_view"] = self.sql_process_view(
            tables["raw_delete_view"], tables["process_delete_view"], keys=[key]
        )
        try:
            SchemaMethods.c_sql_exec_txt(sql["process_delete_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_PROCESS_DELETE_VIEW",
                msg=f"Erreur dans la creation de la vue 'delete_process' pour {key}: {str(e)}",
            )
            return

    def process_relation_data(self, key):
        sm = SchemaMethods(self.schema_code)

        tables = self.tables["relations"][key]
        sql = self.tables["relations"][key]

        property = sm.property(key)
        cor_table = property["schema_dot_table"]
        rel = SchemaMethods(property["schema_code"])

        sql[
            "delete"
        ] = f"""
DELETE FROM {cor_table} t
    USING {tables['process_delete_view']} j
    WHERE t.{sm.pk_field_name()} = j.{sm.pk_field_name()};
"""
        try:
            SchemaMethods.c_sql_exec_txt(sql["delete"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_DELETE",
                msg=f"Erreur dans la suppression pour la relation {key}: {str(e)}",
            )
            return

        # - insert
        sql["insert"] = self.sql_insert(
            tables["process_view"],
            keys=[sm.pk_field_name(), rel.pk_field_name()],
            dest_table=cor_table,
        )
        try:
            SchemaMethods.c_sql_exec_txt(sql["insert"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_INSERT",
                msg=f"Erreur dans l'insertion pour la relation {key}: {str(e)}",
            )
            return
