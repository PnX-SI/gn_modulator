from pathlib import Path
from .utils import ImportMixinUtils
from gn_modulator.schema import SchemaMethods


class ImportMixinMapping(ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    méthodes pour 'mapper' les données
    on va créer une vue intermédaire
    qui va permettre faire le lien entre les colonnes de
    - la table des données (issue d'un fichier csv)
    - la table destinataire

    pour cela on utilise une chaine de caractère qui contient une intruction SELECT
    de cette forme:

        SELECT
            c1_source AS c1_dest,
            ....
        FROM :table_data

    il faut bien utiliser le nom detable ':table_data'
    """

    def mapping_from_file(self):
        """
        récupération du mapping à partir du fichier
        """

        if not Path(self.mapping_file_path).exists():
            self.add_error(
                code="ERR_IMPORT_MAPPING_FILE_MISSING",
                msg=f"Le fichier de preprocess {self.mapping_file_path} n'existe pas",
            )
            return

        with open(self.mapping_file_path, "r") as f:
            self.mapping = f.read()

    def process_mapping_view(self):
        """
        Contruction de la vue de mapping
        le mapping peut venir
        - de l'attribut mapping
        - du fichier mapping_file_path
        """

        # si pas de mapping ou mapping_file_path
        # on passe cette etape
        if not (self.mapping or self.mapping_file_path):
            return

        # si l'attribut mapping n'est pas défini
        # et que l'on a un fichier de mapping
        # on le récupère à partir du fichier
        if (not self.mapping) and self.mapping_file_path:
            self.mapping_from_file()
            if self.errors:
                return

        # nommage de la vue de mapping
        self.tables["mapping"] = self.table_name("mapping")

        # requete de la vue de mapping
        self.sql["mapping_view"] = self.sql_mapping()
        if self.errors:
            return

        # creation de la vue de mapping
        try:
            SchemaMethods.c_sql_exec_txt(self.sql["mapping_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_MAPPING_CREATE_VIEW",
                msg=f"La vue de mapping n'a pas pu être créée : {str(e)}",
            )
            return

        self.count_and_check_table("mapping", self.tables["mapping"])

    def sql_mapping(self):
        """
        requete de creation de la vue de mapping
        """

        # table source : la table des données
        from_table = self.tables["data"]

        # table destinataire : la table de mapping
        dest_table = self.tables["mapping"]

        mapping_select = self.mapping

        # process de la requete
        # pour éviter les problème d'injection sql

        # mise en majuscule de la requete
        mapping_select = mapping_select.upper()

        # on supprime les ';' pour être sur de n'avoir qu'une instruction
        mapping_select = mapping_select.replace(";", "")

        # Pourquoi ???
        mapping_select = mapping_select.replace("%", "%%")

        # Mots interdits pour éviter les instructions non souhaitées
        forbidden_words = []
        for forbidden_word in [
            "INSERT ",
            "DROP ",
            "DELETE ",
            "UPDATE ",
            "EXECUTE ",
            "TRUNCATE ",
            "ALTER ",
            "CREATE ",
            "GRANT ",
            "COPY ",
            "PERFORM ",
        ]:
            if forbidden_word in mapping_select:
                forbidden_words.append(forbidden_word.strip())

        # si présence de mot interdit -> erreur
        if forbidden_words:
            self.add_error(
                code="ERR_IMPORT_MAPPING_FORBIDEN_WORD",
                msg=f"Le fichier de preprocess {self.mapping_file_path} contient le ou les mots interdits {', '.join(forbidden_words)}:\n {mapping_select}",
            )

        # si l'on a pas FROM :TABLE_DATA -> erreur
        if "FROM :TABLE_DATA" not in mapping_select:
            self.add_error(
                code="ERR_IMPORT_MAPPING_MISSING_TABLE",
                msg=f"La selection de mapping doit contenir 'FROM :table_data {mapping_select}",
            )

        # remplacement de ":TABLE_DATA" par la table source
        mapping_select = mapping_select.replace(":TABLE_DATA", from_table)

        # si l'on a pas l'instruction SELECT -> erreur
        if "SELECT" not in mapping_select:
            self.add_error(
                code="ERR_IMPORT_MAPPING_MISSING_SELECT",
                msg=f"La selection de mapping doit contenir 'SELECT {mapping_select}",
            )

        # si la commande select ne contient pas ID_IMPORT -> erreur
        if "ID_IMPORT" not in mapping_select:
            self.add_error(
                code="ERR_IMPORT_MAPPING_MISSING_IMPORT",
                msg=f"La selection de mapping doit contenir le champs 'id_import' dans {self.mapping_file_path}",
            )

        # requete de création de la vue de mapping
        sql_mapping = f"""
DROP VIEW IF EXISTS {dest_table};
CREATE VIEW {dest_table} AS
{mapping_select}
;"""

        return sql_mapping
