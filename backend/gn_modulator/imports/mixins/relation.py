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
        sql_rel = self.sql["relations"][key] = {}
        tables_rel = self.tables["relations"][key] = {}

        # tables["raw_delete_view"] = self.table_name("raw_delete", key)
        tables_rel["delete"] = self.table_name("delete", key)
        # tables["raw_view"] = self.table_name("raw", key)
        tables_rel["process"] = self.table_name("process", key)

        # 0) clean
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables_rel['delete']}")
        SchemaMethods.c_sql_exec_txt(f"DROP VIEW IF EXISTS {tables_rel['process']}")

        sql_rel["process_view"] = self.sql_process_view(
            self.tables["raw"], tables_rel["process"], key_nn=key
        )

        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["process_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_PROCESS_VIEW",
                msg=f"Erreur dans la creation de la vue 'process' pour {key}: {str(e)}",
                key=key,
            )
            return

        sql_rel["delete_view"] = self.sql_process_view(
            self.tables["raw"], tables_rel["delete"], key_nn=key
        )
        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["delete_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_PROCESS_DELETE_VIEW",
                msg=f"Erreur dans la creation de la vue 'delete_process' pour {key}: {str(e)}",
            )
            return

    def process_relation_data(self, key):
        sm = SchemaMethods(self.schema_code)

        tables_rel = self.tables["relations"][key]
        sql_rel = self.tables["relations"][key]

        property = sm.property(key)
        cor_table = property["schema_dot_table"]
        rel = SchemaMethods(property["schema_code"])

        sql_rel[
            "delete"
        ] = f"""
DELETE FROM {cor_table} t
    USING {tables_rel['delete']} j
    WHERE t.{sm.pk_field_name()} = j.{sm.pk_field_name()};
"""
        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["delete"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_DELETE",
                msg=f"Erreur dans la suppression pour la relation {key}: {str(e)}",
            )
            return

        # - insert
        sql_rel["insert"] = self.sql_insert(
            tables_rel["process"],
            keys=[sm.pk_field_name(), rel.pk_field_name()],
            dest_table=cor_table,
        )
        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["insert"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_INSERT",
                msg=f"Erreur dans l'insertion pour la relation {key}: {str(e)}",
            )
            return
