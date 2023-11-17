from .utils import ImportMixinUtils
from gn_modulator import SchemaMethods


class ImportMixinInsert(ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    Insertion des données traitées (table 'process') dans la table destinataire
    - les données traitées sont prête à être insérées telles quelles
      dans la table destinataire
    - on insère les ligne pour lequelles la valeur de la clé primaire
      dans la table 'process' est à NULL
      (sinon il s'agit de lignes déjà existantes)
    """

    def process_step_insert(self):
        """
        méthode pour l'insertion des données dans la table destinataire
        """

        # la table source est la table 'process'
        # les données peuvent être intégrées telles quelles
        # le format est vérifié et les clé étrangères sont résolues
        from_table = self.tables["process"]

        # s'il n'y a pas de ligne à insérer
        # on passe
        if self.res["nb_insert"] == 0:
            return

        # requete d'insertion des données
        self.sql["insert"] = self.sql_insert(from_table)

        try:
            SchemaMethods.c_sql_exec_txt(self.sql["insert"])
        except Exception as e:
            if isinstance(e, AttributeError):
                raise e
            self.add_error(
                error_code="ERR_IMPORT_INSERT",
                error_msg=f"Erreur durant l'insert de {from_table} vers {self.schema_code} : {str(e)}",
            )

    def sql_insert(self, from_table, dest_table=None, keys=None):
        """
        requete d'insertion des données
        """

        # récupération de la table destinataire
        table_name = dest_table or self.Model().sql_schema_dot_table()

        # list des colonnes à insérer
        # - toutes les colonnes de la table process
        # - sauf celle correspondant à la clé primaire
        columns_select = list(
            filter(
                lambda x: (
                    x in keys
                    if keys is not None
                    else self.Model().is_column(x) and not (self.Model().is_primary_key(x))
                ),
                self.get_table_columns(from_table),
            )
        )

        # colonnes selectionées dans la requete d'insert
        txt_columns_select_keys = ",\n    ".join(columns_select)

        # condition pour choisir les lignes à insérer
        # - la clé primaire doit être nulle dans la table source)
        # - il n'y a pas de correspondance avec une ligne existant dans la table destinataire
        txt_where = f" WHERE {self.Model().pk_field_name()} IS NULL" if keys is None else ""

        # requete d'insertion des données
        return f"""INSERT INTO {table_name} (
    {txt_columns_select_keys}
)
SELECT
    {txt_columns_select_keys}
FROM {from_table}{txt_where}
;
"""
