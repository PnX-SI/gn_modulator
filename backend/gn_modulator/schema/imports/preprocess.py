class SchemaPreProcessImports:
    @classmethod
    def import_raw(cls, import_number, schema_code, from_table, dest_table):
        """
        creation de la vue d'import à partir de la table d'import
        correction des null et association du bon typage
        """
        import_txt_create_raw_view = cls.import_txt_create_raw_view(
            import_number, schema_code, from_table, dest_table
        )

        cls.import_set_infos(import_number, schema_code, "sql.raw", import_txt_create_raw_view)
        cls.c_sql_exec_txt(import_txt_create_raw_view)

        cls.count_and_check_table(import_number, schema_code, dest_table, "raw")

    @classmethod
    def import_preprocess(
        cls, import_number, schema_code, from_table, dest_table, pre_process_file_path
    ):
        """
        Application de la vue de mappage à la la table d'import
        """

        if pre_process_file_path is None:
            return

        if not pre_process_file_path.exists():
            cls.import_add_error(
                import_number,
                schema_code,
                code="ERR_IMPORT_PRE_PROCESS_FILE_MISSING",
                msg=f"Le fichier de preprocess {pre_process_file_path} n'existe pas",
            )
            return
        with open(pre_process_file_path, "r") as f:
            txt_pre_process_raw_import_view = (
                f.read()
                .replace(":raw_import_table", from_table)
                .replace(":pre_processed_import_view", dest_table)
                .replace("%", "%%")
            )

            cls.import_set_infos(
                import_number, schema_code, "sql.preprocess", txt_pre_process_raw_import_view
            )
            cls.c_sql_exec_txt(txt_pre_process_raw_import_view)

            cls.count_and_check_table(import_number, schema_code, dest_table, "preprocess")

    @classmethod
    def import_txt_create_raw_view(
        cls,
        import_number,
        schema_code,
        from_table,
        dest_table,
        keys=None,
        key_unnest=None,
        limit=None,
    ):
        """
        - temporary_table : table ou sont stockées les données d'un csv
        - raw_import_view : vue qui corrige les '' en NULL
        Creation d'une vue d'import brute à partir d'une table accueillant des données d'un fichier csv
        on passe les champs valant '' à NULL
        """

        sm = cls(schema_code)

        from_table_columns = cls.get_table_columns(from_table)

        columns = filter(
            lambda x: (
                x in keys
                if keys is not None
                else not (sm.is_column(x) and sm.property(x).get("primary_key"))
            ),
            from_table_columns,
        )

        # on preprocess ttes les colonnes
        v_txt_pre_process_columns = list(
            map(
                lambda x: cls(schema_code).pre_process_raw_import_columns(
                    x, key_unnest=key_unnest
                ),
                from_table_columns,
            )
        )

        v_txt_columns = list(map(lambda x: cls(schema_code).process_raw_import_column(x), columns))

        txt_primary_column = (
            f"""CONCAT({", '|', ".join(sm.attr('meta.unique'))}) AS {sm.pk_field_name()}"""
        )
        v_txt_columns.insert(0, txt_primary_column)

        txt_columns = ",\n    ".join(v_txt_columns)
        txt_pre_process_columns = ",\n    ".join(v_txt_pre_process_columns)
        txt_limit = f"LIMIT {limit}" if limit else ""

        return f"""DROP VIEW IF EXISTS {dest_table} CASCADE;
CREATE VIEW {dest_table} AS
WITH pre_process AS (
SELECT
    {txt_pre_process_columns}
FROM {from_table}
{txt_limit}
)
SELECT
    {txt_columns}
FROM pre_process;
"""

    def pre_process_raw_import_columns(self, key, key_unnest=None):
        """ """

        if key == "id_import":
            return key

        if key_unnest == key:
            return f"UNNEST(STRING_TO_ARRAY({key}, ',')) AS {key}"

        if not self.has_property(key):
            return f"{key}"

        property = self.property(key)
        if property.get("foreign_key"):
            return key

        if property["type"] == "number":
            return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key}::FLOAT END AS {key}"

        if property["type"] == "date":
            return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key}::DATE END AS {key}"

        if property["type"] == "datetime":
            return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key}::TIMESTAMP END AS {key}"

        if property["type"] == "integer" and "schema_code" not in property:
            return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key}::INTEGER END AS {key}"

        return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key} END AS {key}"
