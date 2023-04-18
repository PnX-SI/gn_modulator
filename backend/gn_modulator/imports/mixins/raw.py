from gn_modulator import SchemaMethods
from .utils import ImportMixinUtils


class ImportMixinRaw(ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    creation de la vue 'raw'
    'raw' comme brute car les clé étrangères ou primaires ne sont pas résolues

    - a partir de la table des données 'data'
      ou de la table de mapping 'mapping'

    - on ne selectionne que les colonnes
      - id_import
      - qui sont dans la table destinataire
      - ou qui correspondent à une relation n-n

    - on associe le bon typage au données

    - on traite la geometry en x y si
      - les champs x et y sont présents
      - et le champs geometrie n'est pas présent
    """

    def process_raw_view(self):
        """
        creation de la vue d'import brute
        """

        # table source : mapping si elle existe ou données
        from_table = self.tables.get("mapping") or self.tables["data"]

        # table destinataire: 'raw'
        dest_table = self.tables["raw"] = self.table_name("raw")

        self.sql["raw_view"] = self.sql_raw_view(from_table, dest_table)
        try:
            SchemaMethods.c_sql_exec_txt(self.sql["raw_view"])

        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_CREATE_RAW_VIEW",
                error_msg=f"Erreur dans la creation de la vue 'raw': {str(e)}",
            )

        # comptage et vérification de l'intégrité de la table
        self.count_and_check_table("raw", dest_table)

    def sql_raw_view(
        self,
        from_table,
        dest_table,
        limit=None,
    ):
        """
        script de creation de la vue d'import 'raw'
        """

        sm = SchemaMethods(self.schema_code)

        # colonnes de la table source
        from_table_columns = self.get_table_columns(from_table)

        # colonnes de la table source
        # qui sont dans la table destinataire
        # ou qui sont associée à une relation n-n
        # ou les colonnes ["id_import", "x", "y"]
        columns = list(
            filter(
                lambda x: sm.is_column(x) or sm.is_relation_n_n(x) or x in ["id_import", "x", "y"],
                from_table_columns,
            )
        )

        if sm.pk_field_name() not in columns:
            columns.append(sm.pk_field_name())

        # traitement des colonnes
        # - typage
        # - geometry
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

        # textes sql des colonnes
        txt_columns = ",\n    ".join(v_txt_columns)

        # textes sql pour la limite
        txt_limit = f"\nLIMIT {limit}" if limit else ""

        # requete creation de la vue 'raw'
        return f"""DROP VIEW IF EXISTS {dest_table} CASCADE;
CREATE VIEW {dest_table} AS
SELECT
    {txt_columns}
FROM {from_table} t{txt_limit};
"""

    def txt_geom_xy(self):
        """
        process de la geometrie
        à partir des colonnes 'x' et 'y'
        """
        sm = SchemaMethods(self.schema_code)

        # clé de la colonne geometrie
        geom_key = sm.geometry_field_name()

        # srid associé à la colonne geometrie
        srid_column = sm.property(geom_key).get("srid")

        # srid de l'input
        # - précisé en option
        # - ou celui de la colonne par defaut
        srid_input = self.options.get("srid") or srid_column

        # texte sql pour la colonne geom
        txt_geom = f"""ST_SETSRID(ST_MAKEPOINT(x::FLOAT, y::FLOAT),{srid_input})"""

        # si le srid_d'entrée est différent du srid de la colonne
        # on utilise ST_TRANSFORM
        if srid_input != srid_column:
            txt_geom = f"""ST_TRANSFORM({txt_geom}, {srid_column})"""

        # ajout de l'alias AS {geom_key}
        txt_geom += f" AS {geom_key}"

        return txt_geom

    def process_raw_import_column_geom(self, key):
        """
        process de la geometrie
        - format d'entrée : WKT
          (doit marcher avec le WKB)
        """

        sm = SchemaMethods(self.schema_code)
        property = sm.property(key)

        # srid de la colonne
        srid_column = sm.property(key)["srid"]

        # srid des données
        # - à préciser en options
        # - ou par défaut celui de la colonne
        srid_input = self.options.get("srid") or srid_column

        # texte sql pour la geometrie
        txt_geom = f"""ST_SETSRID(ST_FORCE2D({key}::GEOMETRY), {srid_input})"""

        # pour les multipolygones (par exemple ref_geo.l_area.geom)
        if property["geometry_type"] == "multipolygon":
            txt_geom = f"ST_MULTI({txt_geom})"

        # si le srid d'entrée est différent du srid de la colonne
        if srid_input != srid_column:
            txt_geom = f"ST_TRANSFORM({txt_geom}, {srid_column})"

        # ajout de l'alias
        txt_geom += f" AS {key}"

        return txt_geom

    def process_raw_import_column(self, key):
        """
        process des colonnes brutes
        - typage des colonnes
        - traitement de la geometrie
        """

        sm = SchemaMethods(self.schema_code)

        # colonnes de la liste ["id_import", "x", "y"]
        if key in ["id_import", "x", "y"] and not sm.has_property(key):
            return f"t.{key}"

        property = sm.property(key)

        # clé primaire
        # on concatène les champs d'unicité
        # séparés par des '|'
        if property.get("primary_key"):
            txt_uniques = ", '|', ".join(map(lambda x: f"t.{x}", sm.attr("meta.unique")))
            return f"""CONCAT({txt_uniques}) AS {sm.pk_field_name()}"""

        # clé étrangère ou relation n-n : on renvoie tel quel
        if sm.is_foreign_key(key) or sm.is_relation_n_n(key):
            return f"t.{key}"

        # geometrie
        if property["type"] == "geometry":
            return self.process_raw_import_column_geom(key)

        # pour tous les cas suivants
        # typage sql

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

        if property["type"] == "string":
            return f"{key}"

        raise SchemaMethods.errors.SchemaImportError(
            f"process_raw_import_column, type non traité {self.schema_code} {key} {property}"
        )
