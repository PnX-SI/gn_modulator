class SchemaRelationImports:
    @classmethod
    def import_relations(
        cls, import_number, schema_code, from_table, data_file_path, verbose=None
    ):
        sm = cls(schema_code)

        columns = cls.get_table_columns(from_table)

        for index, key in enumerate(columns):
            if not sm.is_relationship(key):
                continue
            property = sm.property(key)

            # on commence par les n-n
            if property.get("relation_type") in ("n-n"):
                print(f"       process relation n-n {key}")
                cls.import_relation_n_n(import_number, schema_code, from_table, key, verbose)

    @classmethod
    def import_relation_n_n(cls, import_number, schema_code, from_table, key, verbose=None):
        sm = cls(schema_code)

        property = sm.property(key)
        cor_table = property["schema_dot_table"]
        rel = cls(property["schema_code"])

        raw_delete_view = cls.import_table_name(import_number, schema_code, "raw_delete", key)
        process_delete_view = cls.import_table_name(
            import_number, schema_code, "process_delete", key
        )
        raw_import_view = cls.import_table_name(import_number, schema_code, "raw", key)
        process_import_view = cls.import_table_name(import_number, schema_code, "process", key)

        # 0) clean

        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {process_delete_view}")
        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {raw_delete_view}")
        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {process_import_view}")
        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {raw_import_view}")

        # 1) create raw_temp_table for n-n
        txt_raw_unnest_table = cls.import_txt_create_raw_view(
            import_number, schema_code, from_table, raw_import_view, keys=[key], key_unnest=key
        )
        cls.c_sql_exec_txt(txt_raw_unnest_table)
        txt_process_table = cls.import_txt_processed_view(
            import_number, schema_code, raw_import_view, process_import_view, keys=[key]
        )

        cls.c_sql_exec_txt(txt_process_table)

        # 3) insert / update / delete ??

        # - delete : tout depuis import_table
        # create_view for delete
        txt_raw_delete_table = cls.import_txt_create_raw_view(
            import_number, schema_code, from_table, raw_delete_view, keys=[]
        )
        cls.c_sql_exec_txt(txt_raw_delete_table)

        txt_processed_delete_table = cls.import_txt_processed_view(
            import_number, schema_code, raw_delete_view, process_delete_view, keys=[]
        )
        cls.c_sql_exec_txt(txt_processed_delete_table)

        txt_delete = f"""
DELETE FROM {cor_table} t
    USING {process_delete_view} j
    WHERE t.{sm.pk_field_name()} = j.{sm.pk_field_name()};
    """

        cls.c_sql_exec_txt(txt_delete)

        # - insert
        txt_insert = cls.import_txt_insert(
            schema_code,
            process_import_view,
            keys=[sm.pk_field_name(), rel.pk_field_name()],
            dest_table=cor_table,
        )
        cls.c_sql_exec_txt(txt_insert)
