from gn_modulator import SchemaMethods
from .utils import ImportMixinUtils


class ImportMixinRaw(ImportMixinUtils):
    def process_raw_view(self):
        """
        creation de la vue d'import à partir de la table d'import
        correction des null et association du bon typage
        """

        from_table = self.tables.get("mapping") or self.tables["data"]
        dest_table = self.tables["raw"] = self.table_name("raw")
        self.tables = self.tables
        self.sql["raw_view"] = self.sql_raw_view(from_table, dest_table)
        try:
            SchemaMethods.c_sql_exec_txt(self.sql["raw_view"])

        except Exception as e:
            print(self.sql["raw_view"])
            self.add_error(
                code="ERR_IMPORT_CREATE_RAW_VIEW",
                msg=f"Erreur dans la creation de la vue 'raw': {str(e)}",
            )

        self.count_and_check_table("raw", dest_table)

    def sql_raw_view(
        self,
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

        sm = SchemaMethods(self.schema_code)

        from_table_columns = self.get_table_columns(from_table)
        columns = list(
            filter(
                lambda x: (
                    x in keys
                    if keys is not None
                    else (
                        sm.has_property(x)
                        and (
                            (not sm.property(x).get("primary_key"))
                            or sm.property(x).get("relation_type") == "n-n"
                        )
                    )
                ),
                from_table_columns,
            )
        )

        # on preprocess ttes les colonnes
        v_txt_pre_process_columns = list(
            map(
                lambda x: self.pre_process_raw_import_columns(x, key_unnest=key_unnest),
                from_table_columns,
            )
        )

        v_txt_columns = list(map(lambda x: self.process_raw_import_column(x), columns))

        # traitement de la geometrie en x y
        # si des champs x et y sont présents
        # s'il n'y a pas de champs geom
        if (
            sm.geometry_field_name()
            and sm.geometry_field_name() not in columns
            and "x" in from_table_columns
            and "y" in from_table_columns
        ):
            v_txt_pre_process_columns.append(self.txt_geom_xy())
            v_txt_columns.append(sm.geometry_field_name())

        txt_primary_column = f"""CONCAT({", '|', ".join(
                map(
                    lambda x: f"pp.{x}",
                    sm.attr('meta.unique')))}) AS {sm.pk_field_name()}"""
        v_txt_columns.insert(0, txt_primary_column)

        txt_columns = ",\n    ".join(v_txt_columns)
        txt_pre_process_columns = ",\n    ".join(v_txt_pre_process_columns)
        txt_limit = f"\nLIMIT {limit}" if limit else ""

        if "id_import" not in txt_pre_process_columns:
            txt_pre_process_columns = f"id_import, {txt_pre_process_columns}"

        if "id_import" not in txt_columns:
            txt_columns = f"id_import, {txt_columns}"

        return f"""DROP VIEW IF EXISTS {dest_table} CASCADE;
CREATE VIEW {dest_table} AS
WITH pre_process AS (
SELECT
    {txt_pre_process_columns}
FROM {from_table}{txt_limit}
)
SELECT
    {txt_columns}
FROM pre_process pp;
"""

    def txt_geom_xy(self):
        sm = SchemaMethods(self.schema_code)
        srid_column = sm.property(sm.geometry_field_name()).get("srid")

        if self.options.get("srid") and srid_column != self.options.get("srid"):
            return f"""ST_TRANSFORM(
    ST_SETSRID(
        ST_MAKEPOINT(x::FLOAT, y::FLOAT),
        {self.options.get('srid')}
    ),
    {srid_column}
) as {sm.geometry_field_name()}"""

        return f"""ST_SETSRID(
    ST_MAKEPOINT(x::FLOAT, y::FLOAT),
    {srid_column}
    ) as {sm.geometry_field_name()}"""

    def pre_process_raw_import_columns(self, key, key_unnest=None):
        """
        TODO gérer les null dans l'import csv (ou dans l'insert)
        """

        sm = SchemaMethods(self.schema_code)

        if key == "id_import":
            return key

        if key_unnest == key:
            return f"UNNEST(STRING_TO_ARRAY({key}, ',')) AS {key}"

        if not sm.has_property(key):
            return f"{key}"

        property = sm.property(key)
        if property.get("foreign_key"):
            return key

        if property["type"] == "geometry":
            geometry_type = "ST_MULTI(" if property["geometry_type"] == "multipolygon" else ""
            last_par = ")" if geometry_type else ""
            if self.options.get("srid") and self.options.get("srid") != sm.property(key).get(
                "srid"
            ):
                return f"""ST_TRANSFORM({geometry_type}
        ST_SETSRID(
            ST_FORCE2D(
                {key}::GEOMETRY
            ), {self.options.get('srid')}
        ),
        {sm.property(key).get('srid')}
    ){last_par} AS {key}"""

            return f"""{geometry_type}ST_SETSRID(
        ST_FORCE2D(
            {key}::GEOMETRY
        ), {sm.property(key).get('srid')}
    ){last_par} AS {key}"""

        if property["type"] == "number":
            return f"({key})::FLOAT"

        if property["type"] == "boolean":
            f"({key})::BOOLEAN"

        if property["type"] == "date":
            return f"({key})::DATE"

        if property["type"] == "datetime":
            return f"({key})::TIMESTAMP"

        if property["type"] == "integer" and "schema_code" not in property:
            return f"({key})::INTEGER"

        return f"{key}"

    def process_raw_import_column(self, key):
        """ """

        sm = SchemaMethods(self.schema_code)

        if not sm.has_property(key):
            return f"pp.{key}"

        property = sm.property(key)

        # pour les nomenclature (on rajoute le type)
        if nomenclature_type := property.get("nomenclature_type"):
            return f"""CASE
        WHEN pp.{key} IS NOT NULL AND pp.{key} NOT LIKE '%%|%%' THEN CONCAT('{nomenclature_type}|', {key})
        ELSE pp.{key}
    END AS {key}"""

        return f"pp.{key}"
