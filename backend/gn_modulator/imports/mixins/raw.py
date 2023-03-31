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
                    else (sm.has_property(x) or x in ["id_import", "x", "y"])
                ),
                from_table_columns,
            )
        )

        columns.append(sm.pk_field_name())

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
            v_txt_columns.append(self.txt_geom_xy())

        # txt_primary_column = f"""CONCAT({", '|', ".join(
        #         map(
        #             lambda x: f"pp.{x}",
        #             sm.attr('meta.unique')))}) AS {sm.pk_field_name()}"""
        # v_txt_columns.insert(0, txt_primary_column)

        txt_columns = ",\n    ".join(v_txt_columns)
        txt_limit = f"\nLIMIT {limit}" if limit else ""

        columns_nn_nomenclature = list(
            filter(
                lambda x: sm.is_relation_n_n(x) and sm.property(x).get("nomenclature_type"),
                columns,
            )
        )

        v_with_n_n_nomenclature = list(
            map(
                lambda x: self.process_raw_import_with_n_n_nomenclature(x, from_table),
                columns_nn_nomenclature,
            )
        )

        v_join_n_n_nomenclature = list(
            map(
                lambda x: self.process_raw_import_join_n_n_nomenclature(x), columns_nn_nomenclature
            )
        )

        txt_with_n_n_nomenclature = (
            "WITH " + ", ".join(v_with_n_n_nomenclature) if v_with_n_n_nomenclature else ""
        )
        txt_join_n_n_nomenclature = (
            "\n".join(v_join_n_n_nomenclature) + "\n" if v_join_n_n_nomenclature else ""
        )

        return f"""DROP VIEW IF EXISTS {dest_table} CASCADE;
CREATE VIEW {dest_table} AS
{txt_with_n_n_nomenclature}
SELECT
    {txt_columns}
FROM {from_table} t
{txt_join_n_n_nomenclature}{txt_limit};
"""

    def txt_geom_xy(self):
        sm = SchemaMethods(self.schema_code)
        geom_key = sm.geometry_field_name()
        srid_column = sm.property(geom_key).get("srid")
        srid_input = self.options.get("srid") or srid_column
        txt_geom = f"""ST_SETSRID(ST_MAKEPOINT(x::FLOAT, y::FLOAT),{srid_input})"""

        if srid_input != srid_column:
            txt_geom = f"""ST_TRANSFORM({txt_geom}, {srid_column})"""

        txt_geom += f" AS {geom_key}"
        return txt_geom

    def process_raw_import_with_n_n_nomenclature(self, key, from_table):
        return f"""rel_nnu_{key} AS (
    SELECT
        t.id_import,
        UNNEST(STRING_TO_ARRAY(t.{key}, ',')) AS {key}
        FROM {from_table} t
), rel_nn_{key} AS (SELECT
    t.id_import,
    STRING_AGG({self.process_raw_import_column_foreign_key_nomenclature(key)}, ',') AS {key}
    FROM rel_nnu_{key} t
    GROUP BY id_import
)"""

    def process_raw_import_join_n_n_nomenclature(self, key):
        return f"""LEFT JOIN rel_nn_{key} ON rel_nn_{key}.id_import = t.id_import"""

    def process_raw_import_relation_n_n(self, key):
        sm = SchemaMethods(self.schema_code)
        property = sm.property(key)
        if property.get("nomenclature_type"):
            return f"rel_nn_{key}.{key}"
        return f"t.{key}"

    def process_raw_import_column_foreign_key_nomenclature(self, key):
        sm = SchemaMethods(self.schema_code)
        property = sm.property(key)
        nomenclature_type = property.get("nomenclature_type")
        return f"""CASE
        WHEN t.{key} IS NOT NULL AND t.{key} NOT LIKE '%%|%%' THEN CONCAT('{nomenclature_type}|', t.{key})
        ELSE t.{key}
    END"""

    def process_raw_import_column_foreing_key(self, key):
        sm = SchemaMethods(self.schema_code)
        property = sm.property(key)
        if property.get("nomenclature_type"):
            return f"{self.process_raw_import_column_foreign_key_nomenclature(key)} AS {key}"
        return f"t.{key}"

    def process_raw_import_column_geom(self, key):
        sm = SchemaMethods(self.schema_code)
        property = sm.property(key)
        srid_column = sm.property(key)["srid"]
        srid_input = self.options.get("srid") or srid_column

        txt_geom = f"""ST_SETSRID(ST_FORCE2D({key}::GEOMETRY), {srid_input})"""
        if property["geometry_type"] == "multipolygon":
            txt_geom = f"ST_MULTI({txt_geom})"

        if srid_input != srid_column:
            txt_geom = f"ST_TRANSFORM({txt_geom}, {srid_column})"

        txt_geom += f" AS {key}"

        return txt_geom

    def process_raw_import_column(self, key):
        """
        TODO gérer les null dans l'import csv (ou dans l'insert)
        """
        sm = SchemaMethods(self.schema_code)

        if key in ["id_import", "x", "y"] and not sm.has_property(key):
            return f"t.{key}"

        property = sm.property(key)

        if property.get("primary_key"):
            return f"""CONCAT({", '|', ".join(
                map(
                    lambda x: f"t.{x}",
                    sm.attr('meta.unique')))}) AS {sm.pk_field_name()}"""

        if property["type"] == "integer" and property.get("foreign_key"):
            return self.process_raw_import_column_foreing_key(key)

        if property["type"] == "relation" and property["relation_type"] == "n-n":
            return self.process_raw_import_relation_n_n(key)

        if property["type"] == "geometry":
            return self.process_raw_import_column_geom(key)

        if property["type"] == "number":
            return f"{key}::FLOAT"

        if property["type"] == "boolean":
            return f"{key}::BOOLEAN"

        if property["type"] == "uuid":
            return f"{key}::UUID"

        if property["type"] == "date":
            return f"{key}::DATE"

        if property["type"] == "datetime":
            return f"{key}::TIMESTAMP"

        if property["type"] == "integer":
            return f"{key}::INTEGER"

        if property["type"] == "integer":
            return f"{key}::INTEGER"

        return f"{key}"
