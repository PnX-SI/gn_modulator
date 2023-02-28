class SchemaUpdateImports:
    @classmethod
    def import_update(cls, import_number, schema_code, from_table):
        nb_update = cls.c_sql_exec_txt(cls.import_txt_nb_update(schema_code, from_table)).scalar()

        cls.import_set_infos(import_number, schema_code, "nb_update", nb_update)

        if nb_update == 0:
            return

        try:
            import_txt_update = cls.import_txt_update(schema_code, from_table)
            cls.import_set_infos(import_number, schema_code, "sql.update", nb_update)
            cls.c_sql_exec_txt(import_txt_update)
        except Exception as e:
            cls.import_add_error(
                import_number,
                schema_code,
                code="ERR_IMPORT_UPDATE",
                msg=f"Erreur durant l'insert de {from_table} vers {schema_code} : {str(e)}",
            )

    @classmethod
    def import_txt_update(cls, schema_code, processed_import_view):
        sm = cls(schema_code)

        columns = cls.get_table_columns(processed_import_view)

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
    FROM {processed_import_view}
)a
WHERE a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
AND {txt_update_conditions}
;
"""

    @classmethod
    def import_txt_nb_update(cls, schema_code, processed_import_view):
        sm = cls(schema_code)

        columns = cls.get_table_columns(processed_import_view)

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
    JOIN {processed_import_view} a
        ON a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
    WHERE {txt_update_conditions}
;
"""
