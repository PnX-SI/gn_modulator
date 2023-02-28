class SchemaInsertImports:
    @classmethod
    def import_insert(cls, import_number, schema_code, from_table):
        sm = cls(schema_code)
        nb_insert = cls.c_sql_exec_txt(
            f"SELECT COUNT(*) FROM {from_table} WHERE {sm.pk_field_name()} IS NULL"
        ).scalar()

        cls.import_set_infos(import_number, schema_code, "nb_insert", nb_insert)

        if not nb_insert:
            return

        try:
            import_txt_insert = cls.import_txt_insert(schema_code, from_table)
            cls.import_set_infos(import_number, schema_code, "sql.insert", nb_insert)
            cls.c_sql_exec_txt(import_txt_insert)
        except Exception as e:
            if isinstance(e, AttributeError):
                raise e
            cls.import_add_error(
                import_number,
                schema_code,
                code="ERR_IMPORT_INSERT",
                msg=f"Erreur durant l'insert de {from_table} vers {schema_code} : {str(e)}",
            )

    @classmethod
    def import_txt_insert(cls, schema_code, from_table, dest_table=None, keys=None):
        sm = cls(schema_code)

        table_name = dest_table or sm.sql_schema_dot_table()

        columns_select = filter(
            lambda x: (
                x in keys
                if keys is not None
                else not (sm.is_column(x) and sm.property(x).get("primary_key"))
            ),
            cls.get_table_columns(from_table),
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
