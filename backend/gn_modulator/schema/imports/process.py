class SchemaProcessImports:
    @classmethod
    def import_process(cls, import_number, schema_code, from_table, dest_table, keys=None):
        import_txt_processed_view = cls.import_txt_processed_view(
            import_number, schema_code, from_table, dest_table, keys
        )

        cls.import_set_infos(import_number, schema_code, "sql.process", import_txt_processed_view)

        cls.c_sql_exec_txt(import_txt_processed_view)

        cls.count_and_check_table(import_number, schema_code, dest_table, "process")

    @classmethod
    def import_txt_processed_view(
        cls, import_number, schema_code, from_table, dest_table, keys=None
    ):
        """
        requete pour créer une vue qui résoud les clé
        """

        sm = cls(schema_code)

        v_columns = []
        v_joins = []

        from_table_columns = cls.get_table_columns(from_table)

        columns = list(
            filter(
                lambda x: (
                    x in keys
                    if keys is not None
                    else sm.is_column(x) and not sm.property(x).get("primary_key")
                ),
                from_table_columns,
            )
        )

        solved_keys = {}

        for index, key in enumerate(columns):
            txt_column, v_join = sm.process_column_import_view(index, key)
            if txt_column:
                # TODO n-n ici ????
                if sm.has_property(key) and sm.property(key).get("relation_type") == "n-n":
                    rel = cls(sm.property(key)["schema_code"])
                    v_columns.append(f"{txt_column.split('.')[0]}.{rel.pk_field_name()}")
                else:
                    v_columns.append(f"{txt_column} AS {key}")
            solved_keys[key] = txt_column
            v_joins += v_join

        txt_pk_column, v_join = sm.resolve_key(
            sm.pk_field_name(), alias_join_base="j_pk", solved_keys=solved_keys
        )
        v_columns.append(txt_pk_column)
        v_joins += v_join

        txt_columns = ",\n    ".join(v_columns)
        txt_joins = "\n".join(v_joins)

        return f"""DROP VIEW IF EXISTS {dest_table} CASCADE;
CREATE VIEW {dest_table} AS
SELECT
    {txt_columns}
FROM {from_table} t
{txt_joins};
"""

    def process_raw_import_column(self, key):
        """ """
        if not self.has_property(key):
            return f"{key}"

        property = self.property(key)

        # pour les nomenclature (on rajoute le type)
        if nomenclature_type := property.get("nomenclature_type"):
            return f"""CASE
        WHEN {key} IS NOT NULL AND {key} NOT LIKE '%%|%%' THEN CONCAT('{nomenclature_type}|', {key})
        ELSE {key}
    END AS {key}"""

        if property["type"] == "boolean":
            return f"""CASE
        WHEN {key}::text IN ('t', 'true') THEN TRUE
        WHEN {key}::text IN ('f', 'false') THEN FALSE
        ELSE NULL
    END AS {key}"""

        if property["type"] == "geometry":
            geometry_type = "ST_MULTI" if property["geometry_type"] == "multipolygon" else ""
            return f"""{geometry_type}(
        ST_SETSRID(
            ST_FORCE2D(
                ST_GEOMFROMEWKT({key})
            ), {self.property(key).get('srid')}
        )
    )
    AS {key}"""

        return f"{key}"

    def resolve_key(self, key, index=None, alias_main="t", alias_join_base="j", solved_keys={}):
        """
        compliqué
        crée le txt pour
            le champs de la colonne qui doit contenir la clé
            la ou les jointures nécessaire pour résoudre la clé
        """

        alias_join = alias_join_base if index is None else f"{alias_join_base}_{index}"

        txt_column = f"{alias_join}.{self.pk_field_name()}"

        unique = self.attr("meta.unique")
        v_join = []

        # resolution des cles si besoins

        # couf pour permttre de faire les liens entre les join quand il y en a plusieurs
        link_joins = {}
        for index_unique, k_unique in enumerate(unique):
            var_key = self.var_key(key, k_unique, index_unique, link_joins, alias_main)
            if self.property(k_unique).get("foreign_key"):
                if k_unique in solved_keys:
                    link_joins[k_unique] = solved_keys[k_unique]
                else:
                    rel = self.cls(self.property(k_unique)["schema_code"])
                    txt_column_join, v_join_inter = rel.resolve_key(
                        var_key,
                        index=index_unique,
                        alias_main=alias_join,
                        alias_join_base=alias_join,
                    )
                    v_join += v_join_inter

                    link_joins[k_unique] = f"{alias_join}_{index_unique}.{rel.pk_field_name()}"

        # creation des joins avec les conditions
        v_join_on = []

        for index_unique, k_unique in enumerate(unique):
            var_key = self.var_key(key, k_unique, index_unique, link_joins, alias_main)
            # !!!(SELECT (NULL = NULL) => NULL)
            cast = "::TEXT"  # if var_type != main_type else ''
            txt_join_on = (
                f"{alias_join}.{k_unique}{cast} = {var_key}{cast}"
                if not self.is_nullable(k_unique) or self.is_required(k_unique)
                else f"({alias_join}.{k_unique}{cast} = {var_key}{cast} OR ({alias_join}.{k_unique} IS NULL AND {var_key} IS NULL))"
                # else f"({var_key} IS NOT NULL) AND ({alias_join}.{k_unique} = {var_key})"
            )
            v_join_on.append(txt_join_on)

        txt_join_on = "\n        AND ".join(v_join_on)
        txt_join = f"LEFT JOIN {self.sql_schema_dot_table()} {alias_join} ON\n      {txt_join_on}"

        v_join.append(txt_join)

        return txt_column, v_join

    def var_key(self, key, k_unique, index_unique, link_joins, alias_main):
        """
        TODO à clarifier
        """

        if key is None:
            return f"{alias_main}.{k_unique}"

        if link_joins.get(k_unique):
            return link_joins[k_unique]

        if "." in key:
            return key

        if len(self.attr("meta.unique", [])) <= 1:
            return f"{alias_main}.{key}"

        return f"SPLIT_PART({alias_main}.{key}, '|', { index_unique + 1})"

    def process_column_import_view(self, index, key):
        """
        process column for processed view
        """
        if not self.has_property(key):
            return key, []

        property = self.property(key)

        if property.get("foreign_key"):
            rel = self.cls(property["schema_code"])
            return rel.resolve_key(key, index)

        if property.get("relation_type") == "n-n":
            rel = self.cls(property["schema_code"])
            return rel.resolve_key(key, index)

            # txt_column, v_join = rel.resolve_key(key, index)
            # return f"{txt_column.split('.')[0]}.{rel.pk_field_name()}", v_join

        return f"t.{key}", []
