from .utils import ImportMixinUtils
from gn_modulator import SchemaMethods


class ImportMixinUpdate(ImportMixinUtils):
    def process_update(self):
        from_table = self.tables["process"]

        self.sql["nb_update"] = self.sql_nb_update(from_table)

        try:
            self.res["nb_update"] = SchemaMethods.c_sql_exec_txt(self.sql["nb_update"]).scalar()
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_UPDATE_COUNT",
                msg=f"Erreur lors du comptage du nombre d'update: {str(e)}",
            )
            return

        if self.res["nb_update"] == 0:
            return

        self.sql["update"] = self.sql_update(from_table)

        try:
            SchemaMethods.c_sql_exec_txt(self.sql["update"])
        except Exception as e:
            if isinstance(e, AttributeError):
                raise e
            self.add_error(
                code="ERR_IMPORT_UPDATE",
                msg=f"Erreur durant l'update de {from_table} vers {self.schema_code} : {str(e)}",
            )

    def sql_update(self, from_table):
        sm = SchemaMethods(self.schema_code)

        columns = self.get_table_columns(from_table)

        v_column_keys = map(
            lambda x: x,
            filter(lambda x: sm.has_property(x) and sm.is_column(x), columns),
        )

        v_set_keys = list(
            map(
                lambda x: f"{x}=a.{x}",
                filter(
                    lambda x: sm.has_property(x)
                    and sm.is_column(x)
                    and not sm.property(x).get("primary_key"),
                    columns,
                ),
            )
        )

        v_update_condition = list(
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

        txt_set_keys = ",\n    ".join(v_set_keys)
        txt_columns_keys = ",\n        ".join(v_column_keys)
        txt_update_conditions = "NOT (" + "\n    AND ".join(v_update_condition) + ")"

        return f"""
UPDATE {sm.sql_schema_dot_table()} t SET
    {txt_set_keys}
FROM (
    SELECT
        {txt_columns_keys}
    FROM {from_table}
)a
WHERE a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
AND {txt_update_conditions}
;
"""

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

        return f"""
    SELECT
        COUNT(*)
    FROM {sm.sql_schema_dot_table()} t
    JOIN {from_table} a
        ON a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
    WHERE {txt_update_conditions}
;
"""
