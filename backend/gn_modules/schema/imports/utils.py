from geonature.utils.env import db
from utils_flask_sqla.generic import GenericTable


class SchemaUtilsImports:
    """
    methodes pour aider aux imports
    """

    @classmethod
    def clean_import(cls, raw_import_view):
        """ """

        db.engine.execute(f"DROP TABLE IF EXISTS {raw_import_view} CASCADE")

    @classmethod
    def txt_create_temporary_table_for_csv_import(cls, temporary_table, first_line):
        """
        requete de creation d'une table temporaire pour import csv
        tout les champs sont en varchar
        """

        # pour avoir le nom des champs de la table temporaire
        columns = first_line.replace("\n", "").split(";")
        columns_sql = "\n".join(map(lambda x: f"{x} VARCHAR,", columns))

        return f"""CREATE TABLE IF NOT EXISTS {temporary_table} (
    id_import SERIAL NOT NULL,
    {columns_sql}
    CONSTRAINT pk_{'_'.join(temporary_table.split('.'))}_id_import PRIMARY KEY (id_import)
);"""

    @classmethod
    def txt_pre_process_raw_import_view(
        cls,
        schema_code,
        pre_process_file_path,
        raw_import_table,
        pre_process_import_view,
    ):
        """
        pre-process pour le mapping (csv -> table d'import)
        """

        with open(pre_process_file_path, "r") as f:
            return (
                f.read()
                .replace(":raw_import_table", raw_import_table)
                .replace(":pre_process_import_view", pre_process_import_view)
            )

    @classmethod
    def txt_copy_from_csv(cls, temporary_table, first_line):
        """
        Commande pour effectuer le copy d'un fichier csv dans une table temporaire
        """

        columns = first_line.replace("\n", "").split(";")
        columns_fields = ", ".join(columns)
        return f"COPY {temporary_table}({columns_fields}) FROM STDIN WITH CSV DELIMITER ';' QUOTE '\"';"

    @classmethod
    def get_table_columns(cls, schema_dot_table):
        """
        renvoie les colonnes d'une table identifiée par schema_dot_table
        """
        return GenericTable(
            schema_dot_table.split(".")[1], schema_dot_table.split(".")[0], db.engine
        ).tableDef.columns

    @classmethod
    def txt_create_raw_import_view(
        cls, schema_code, temporary_table, raw_import_view, keys=None, key_unnest=None
    ):
        """
        - temporary_table : table ou sont stockées les données d'un csv
        - raw_import_view : vue qui corrige les '' en NULL
        Creation d'une vue d'import brute à partir d'une table accueillant des données d'un fichier csv
        on passe les champs valant '' à NULL
        """

        sm = cls(schema_code)

        columns = filter(
            lambda x: (
                x.key in keys
                if keys is not None
                else not (sm.is_column(x.key) and sm.property(x.key).get("primary_key"))
            ),
            cls.get_table_columns(temporary_table),
        )

        # on preprocess ttes les colonnes
        v_txt_pre_process_columns = list(
            map(
                lambda x: cls(schema_code).pre_process_raw_import_columns(
                    x.key, key_unnest=key_unnest
                ),
                cls.get_table_columns(temporary_table),
            )
        )

        v_txt_columns = list(
            map(lambda x: cls(schema_code).process_raw_import_column(x.key), columns)
        )

        txt_primary_column = (
            f"""CONCAT({", '|', ".join(sm.attr('meta.unique'))}) AS {sm.pk_field_name()}"""
        )
        v_txt_columns.insert(0, txt_primary_column)

        txt_columns = ",\n    ".join(v_txt_columns)
        txt_pre_process_columns = ",\n    ".join(v_txt_pre_process_columns)

        return f"""DROP VIEW IF EXISTS {raw_import_view} CASCADE;
CREATE VIEW {raw_import_view} AS
WITH pre_process AS (
SELECT
    {txt_pre_process_columns}
FROM {temporary_table}
)
SELECT
    {txt_columns}
FROM pre_process
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

        if property["type"] == "number":
            return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key}::FLOAT END AS {key}"

        if property["type"] == "date":
            return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key}::DATE END AS {key}"

        if property["type"] == "integer" and "schema_code" not in property:
            return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key}::INTEGER END AS {key}"

        return f"CASE WHEN {key}::TEXT = '' THEN NULL ELSE {key} END AS {key}"

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

    @classmethod
    def txt_create_processed_import_view(
        cls, schema_code, raw_import_view, processed_import_view, keys=None
    ):
        """
        requete pour créer une vue qui résoud les clé
        """

        sm = cls(schema_code)

        v_columns = []
        v_joins = []

        columns = filter(
            lambda x: (
                x.key in keys
                if keys is not None
                else sm.is_column(x.key) and not sm.property(x.key).get("primary_key")
            ),
            cls.get_table_columns(raw_import_view),
        )

        solved_keys = {}

        for index, column in enumerate(columns):
            txt_column, v_join = sm.process_column_import_view(index, column.key)
            if txt_column:
                # TODO n-n ici ????
                if (
                    sm.has_property(column.key)
                    and sm.property(column.key).get("relation_type") == "n-n"
                ):
                    rel = cls(sm.property(column.key)["schema_code"])
                    v_columns.append(f"{txt_column.split('.')[0]}.{rel.pk_field_name()}")
                else:
                    v_columns.append(f"{txt_column} AS {column.key}")
            solved_keys[column.key] = txt_column
            v_joins += v_join

        txt_pk_column, v_join = sm.resolve_key(
            sm.pk_field_name(), alias_join_base="j_pk", solved_keys=solved_keys
        )
        v_columns.append(txt_pk_column)
        v_joins += v_join

        txt_columns = ",\n    ".join(v_columns)
        txt_joins = "\n".join(v_joins)

        return f"""DROP VIEW IF EXISTS {processed_import_view} CASCADE;
CREATE VIEW {processed_import_view} AS
SELECT
    {txt_columns}
FROM {raw_import_view} t
{txt_joins}
"""

    def resolve_key(self, key, index=None, alias_main="t", alias_join_base="j", solved_keys={}):
        """
        compliqué
        crée le txt pour
            le champs de la colonne qui doit contenir la clé
            la ou les jointures nécessaire pour résoudre la clé
        """

        alias_join = alias_join_base if index is None else f"{alias_join_base}_{index}"

        txt_column = f"{alias_join}.{self.pk_field_name()}"

        uniques = self.attr("meta.unique")
        v_join = []

        # resolution des cles si besoins

        # couf pour permttre de faire les liens entre les join quand il y en a plusieurs
        link_joins = {}
        for index_unique, k_unique in enumerate(uniques):
            var_key = self.var_key(key, k_unique, index_unique, link_joins, alias_main)

            if self.property(k_unique).get("foreign_key"):
                if k_unique in solved_keys:
                    link_joins[k_unique] = solved_keys[k_unique]
                else:
                    rel = self.cls(self.property(k_unique)["schema_code"])
                    txt_column_join, v_join_inter = rel.resolve_key(
                        var_key,
                        index_unique,
                        alias_main=alias_join,
                        alias_join_base=alias_join,
                    )
                    v_join += v_join_inter

                    link_joins[k_unique] = f"{alias_join}_{index_unique}.{rel.pk_field_name()}"

        # creation des joins avec les conditions
        v_join_on = []

        for index_unique, k_unique in enumerate(uniques):
            var_key = self.var_key(key, k_unique, index_unique, link_joins, alias_main)
            # !!!(SELECT (NULL = NULL) => NULL)
            txt_join_on = (
                f"{alias_join}.{k_unique} = {var_key}"
                if self.is_required(k_unique)
                else f"({alias_join}.{k_unique} = {var_key} OR ({alias_join}.{k_unique} IS NULL AND {var_key} IS NULL))"
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

    @classmethod
    def txt_import_view_to_insert(
        cls, schema_code, processed_import_view, dest_table=None, keys=None
    ):
        sm = cls(schema_code)

        table_name = dest_table or sm.sql_schema_dot_table()

        columns_select = filter(
            lambda x: (
                x.key in keys
                if keys is not None
                else not (sm.is_column(x.key) and sm.property(x.key).get("primary_key"))
            ),
            cls.get_table_columns(processed_import_view),
        )

        v_column_select_keys = map(lambda x: x.key, columns_select)

        txt_columns_select_keys = ",\n    ".join(v_column_select_keys)

        txt_where = f"WHERE {sm.pk_field_name()} IS NULL" if keys is None else ""

        return f"""
INSERT INTO {table_name} (
    {txt_columns_select_keys}
)
SELECT
    {txt_columns_select_keys}
FROM {processed_import_view}

{txt_where};
"""

    @classmethod
    def txt_import_view_to_update(cls, schema_code, processed_import_view):
        sm = cls(schema_code)

        columns = cls.get_table_columns(processed_import_view)

        v_column_keys = map(
            lambda x: x.key,
            filter(lambda x: sm.has_property(x.key) and sm.is_column(x.key), columns),
        )

        v_set_keys = list(
            map(
                lambda x: f"{x.key}=a.{x.key}",
                filter(
                    lambda x: sm.has_property(x.key)
                    and sm.is_column(x.key)
                    and not sm.property(x.key).get("primary_key"),
                    columns,
                ),
            )
        )

        v_update_condition = list(
            map(
                lambda x: f"(t.{x.key} IS DISTINCT FROM a.{x.key})",
                filter(
                    lambda x: sm.has_property(x.key)
                    and sm.is_column(x.key)
                    and not sm.property(x.key).get("primary_key"),
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
    def txt_nb_update(cls, schema_code, processed_import_view):
        sm = cls(schema_code)

        columns = cls.get_table_columns(processed_import_view)

        v_update_conditions = list(
            map(
                lambda x: f"(t.{x.key} IS DISTINCT FROM a.{x.key})",
                filter(
                    lambda x: sm.has_property(x.key)
                    and sm.is_column(x.key)
                    and not sm.property(x.key).get("primary_key"),
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
