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

    def process_step_mapping_view(self):
        """
        Contruction de la vue de mapping
        le mapping peut venir
        - de l'attribut mapping
        """

        # si pas de mapping
        # on passe cette etape
        if not (self.has_mapping()):
            self.mapping_check_and_process_missing_unique()
            self.tables["mapping"] = self.tables.get("mapping") or self.tables["data"]
            return

        # si l'attribut mapping n'est pas défini
        # et que l'on a un fichier de mapping
        # on le récupère à partir du fichier

        # if (not self.mapping) and self.mapping_file_path:
        #     self.mapping_from_file()
        #     if self.errors:
        #         return

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
                error_code="ERR_IMPORT_MAPPING_CREATE_VIEW",
                error_msg=f"La vue de mapping n'a pas pu être créée : {str(e)}",
            )
            return

        self.count_and_check_table("mapping", self.tables["mapping"])

    def mapping_select(self):
        mapping_field = self.mapping_field.value if self.mapping_field else {}
        mapping_value = self.mapping_value.value if self.mapping_value else {}

        columns = self.get_table_columns(self.tables["data"])

        columns_select = []
        keys = []

        for key, value in mapping_field.items():
            if isinstance(value, list):
                values = list(
                    map(
                        lambda x: f"""'"{x}": "', {x}, '"'""",
                        filter(lambda x: x in columns, value),
                    )
                )
                if not values:
                    continue
                processed_value = """, ',', """.join(values)

                concat_for_jsonb = f"""CONCAT('{{', {processed_value},  '}}')"""
                columns_select.append(f"{concat_for_jsonb} AS {key}")

            else:
                if (
                    isinstance(value, str) and all(x not in value for x in ["'", "("])
                ) and value not in columns:
                    continue

                if mapping_value.get(key):
                    case_elements = []
                    for mv_source, mv_target in mapping_value.get(key).items():
                        case_element = f"WHEN {value} = '{mv_source}' then '{mv_target}'"
                        case_elements.append(case_element)
                    case_elements_txt = "\n    ".join(case_elements)
                    mapped_value = f"""CASE\n    {case_elements_txt}\n    ELSE {value} END"""
                    columns_select.append(f"{mapped_value} AS {key}")

                else:
                    columns_select.append(f"{value} AS {key}")
            keys.append(key)

        for key in columns:
            if key not in keys:
                columns_select.append(key)

        sql_columns_select = "\n, ".join(columns_select)

        mapping_select = f"""
        SELECT {sql_columns_select}
        FROM :table_data
        """

        return mapping_select

    def mapping_check_and_process_missing_unique(self):
        # check unique nonrequired
        columns = self.get_table_columns(self.tables["data"])

        missing_uniques = [
            key_unique
            for key_unique in self.sm().unique()
            if self.Model().has_property(key_unique) and key_unique not in columns
        ]

        if len(missing_uniques) == 0:
            return

        self.tables["mapping"] = self.table_name("mapping")

        missing_uniques_txt = "\n    ,".join(map(lambda x: f"NULL AS {x}", missing_uniques))

        self.sql[
            "mapping_view"
        ] = f"""CREATE VIEW {self.tables["mapping"]} AS
SELECT
    *,
    {missing_uniques_txt}
FROM {self.tables["data"]}
"""
        try:
            SchemaMethods.c_sql_exec_txt(self.sql["mapping_view"])
        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_MAPPING_CREATE_VIEW",
                error_msg=f"La vue de mapping n'a pas pu être créée : {str(e)}",
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

        mapping_select = self.mapping_select()

        # process de la requete
        # pour éviter les problème d'injection sql

        # on supprime les ';' pour être sur de n'avoir qu'une instruction
        mapping_select = mapping_select.replace(";", "")

        # Pourquoi ???
        mapping_select = mapping_select.replace("%", "%%")

        # mise en majuscule pour les tests des mots interdits
        mapping_select_upper = mapping_select.upper()

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
            if forbidden_word in mapping_select_upper:
                forbidden_words.append(forbidden_word.strip())

        # si présence de mot interdit -> erreur
        if forbidden_words:
            self.add_error(
                error_code="ERR_IMPORT_MAPPING_FORBIDEN_WORD",
                error_msg=f"Le fichier de preprocess {self.mapping_file_path} contient le ou les mots interdits {', '.join(forbidden_words)}:\n {mapping_select}",
            )

        # si l'on a pas FROM :table_data -> erreur
        if "FROM :table_data" not in mapping_select:
            self.add_error(
                error_code="ERR_IMPORT_MAPPING_MISSING_TABLE",
                error_msg=f"La selection de mapping doit contenir 'FROM :table_data {mapping_select}",
            )

        # remplacement de ":table_data" par la table source
        mapping_select = mapping_select.replace(":table_data", from_table)

        # si l'on a pas l'instruction SELECT -> erreur
        if "SELECT" not in mapping_select_upper:
            self.add_error(
                error_code="ERR_IMPORT_MAPPING_MISSING_SELECT",
                error_msg=f"La selection de mapping doit contenir 'SELECT",
            )

        # si la commande select ne contient pas ID_IMPORT -> erreur
        if "ID_IMPORT" not in mapping_select_upper:
            self.add_error(
                error_code="ERR_IMPORT_MAPPING_MISSING_IMPORT",
                error_msg=f"La selection de mapping doit contenir le champs 'id_import' dans {self.mapping_file_path}",
            )

        # requete de création de la table de mapping
        #
        sql_mapping = f"""
DROP TABLE IF EXISTS {dest_table};
CREATE TABLE {dest_table} AS
{mapping_select}
;"""
        return sql_mapping
