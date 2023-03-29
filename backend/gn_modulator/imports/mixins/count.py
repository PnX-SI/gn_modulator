from gn_modulator import SchemaMethods
from .utils import ImportMixinUtils


class ImportMixinCount(ImportMixinUtils):
    def process_count(self):
        self.count_insert()
        self.count_update()
        self.res["nb_unchanged"] = (
            self.res["nb_process"] - self.res["nb_insert"] - self.res["nb_update"]
        )

    def sql_nb_update(self, from_table):
        sm = SchemaMethods(self.schema_code)

        columns = self.get_table_columns(from_table)

        v_update_conditions = list(
            map(
                lambda x: f"(t.{x}::TEXT IS DISTINCT FROM a.{x}::TEXT)",
                filter(
                    lambda x: sm.has_property(x)
                    and sm.is_column(x)
                    and not sm.property(x).get("primary_key"),
                    columns,
                ),
            )
        )

        txt_update_conditions = "" + "\n    OR ".join(v_update_conditions) + ""

        print(txt_update_conditions)

        return f"""
    SELECT
        COUNT(*)
    FROM {sm.sql_schema_dot_table()} t
    JOIN {from_table} a
        ON a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
    WHERE {txt_update_conditions}
;
"""

    def count_update(self):
        from_table = self.tables["process"]

        self.sql["nb_update"] = self.sql_nb_update(from_table)

        try:
            self.res["nb_update"] = SchemaMethods.c_sql_exec_txt(self.sql["nb_update"]).scalar()
        except Exception as e:
            print(self.sql["nb_update"])
            self.add_error(
                code="ERR_IMPORT_UPDATE_COUNT",
                msg=f"Erreur lors du comptage du nombre d'update: {str(e)}",
            )
        return

    def count_insert(self):
        from_table = self.tables["process"]
        sm = SchemaMethods(self.schema_code)
        self.sql[
            "nb_insert"
        ] = f"SELECT COUNT(*) FROM {from_table} WHERE {sm.pk_field_name()} IS NULL"

        try:
            self.res["nb_insert"] = SchemaMethods.c_sql_exec_txt(self.sql["nb_insert"]).scalar()
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_INSERT_COUNT",
                msg=f"Erreur lors du comptage du nombre d'insert: {str(e)}",
            )
            return
