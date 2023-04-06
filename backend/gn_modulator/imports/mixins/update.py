from .utils import ImportMixinUtils
from gn_modulator import SchemaMethods


class ImportMixinUpdate(ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    gestion de la mise à jour des données
    """

    def process_update(self):
        """
        méthode pour mettre à jour les données
        """

        # source : table process
        from_table = self.tables["process"]

        # script d'update
        self.sql["update"] = self.sql_update(from_table)

        # si le nombre d'update (count.py) est null
        # on passe
        if self.res["nb_update"] == 0:
            return

        # on procède à la mise à jour des données
        try:
            SchemaMethods.c_sql_exec_txt(self.sql["update"])
        except Exception as e:
            if isinstance(e, AttributeError):
                raise e
            self.add_error(
                code="ERR_IMPORT_UPDATE",
                msg=f"Erreur durant l'update de {from_table} vers {self.schema_code} : {str(e)}",
            )

    def sql_update(self, from_table):
        """
        script pour la mise à jour des données
        """
        sm = SchemaMethods(self.schema_code)

        # toutes les colonnes de la table 'process'
        columns = self.get_table_columns(from_table)

        # toutes les colonnes associée à une colonne de la table destinataire
        v_column_keys = list(
            map(
                lambda x: x,
                filter(
                    lambda x: sm.is_column(x) and x != self.id_digitiser_key(),
                    columns,
                ),
            )
        )

        # pour les instructions SET
        # toutes les colonnes sauf la clé primaire
        # et la clé digitiser
        v_set_keys = list(
            map(lambda x: f"{x}=p.{x}", filter(lambda x: not sm.is_primary_key(x), v_column_keys))
        )

        # les condition d'update
        # - pour toutes les colonnes v_set_keys
        # on regarde si la données importée est distincte des données existante
        v_update_condition = list(
            map(
                lambda x: f"(t.{x}::TEXT IS DISTINCT FROM p.{x}::TEXT)",
                v_column_keys,
            )
        )

        # texte sql pour l'instruction SET
        txt_set_keys = ",\n    ".join(v_set_keys)

        # texte sql pour la selection des colonnes de la table process p
        txt_columns_keys = ",\n        ".join(v_column_keys)

        # condition pour voir si une ligne est modifiée
        txt_update_conditions = "NOT (\n    " + "\n    AND ".join(v_update_condition) + "\n)"

        return f"""UPDATE {sm.sql_schema_dot_table()} t SET
    {txt_set_keys}
FROM (
    SELECT
        {txt_columns_keys}
    FROM {from_table}
)p
WHERE p.{sm.pk_field_name()} = t.{sm.pk_field_name()}
  AND {txt_update_conditions}
;
"""
