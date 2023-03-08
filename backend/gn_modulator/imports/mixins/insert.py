from .utils import ImportMixinUtils
from gn_modulator import SchemaMethods


class ImportMixinInsert(ImportMixinUtils):
    def process_insert(self):
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

        if self.res["nb_insert"] == 0:
            return

        self.sql["insert"] = self.sql_insert(from_table)

        try:
            SchemaMethods.c_sql_exec_txt(self.sql["insert"])
        except Exception as e:
            if isinstance(e, AttributeError):
                raise e
            self.add_error(
                code="ERR_IMPORT_INSERT",
                msg=f"Erreur durant l'insert de {from_table} vers {self.schema_code} : {str(e)}",
            )

    def sql_insert(self, from_table, dest_table=None, keys=None):
        sm = SchemaMethods(self.schema_code)

        table_name = dest_table or sm.sql_schema_dot_table()

        columns_select = list(
            filter(
                lambda x: (
                    x in keys
                    if keys is not None
                    else sm.is_column(x) and not (sm.property(x).get("primary_key"))
                ),
                SchemaMethods.get_table_columns(from_table),
            )
        )

        v_column_select_keys = map(lambda x: x, columns_select)

        txt_columns_select_keys = ",\n    ".join(v_column_select_keys)

        txt_where = f" WHERE {sm.pk_field_name()} IS NULL" if keys is None else ""

        return f"""
INSERT INTO {table_name} (
    {txt_columns_select_keys}
)
SELECT
    {txt_columns_select_keys}
FROM {from_table}{txt_where};
"""
