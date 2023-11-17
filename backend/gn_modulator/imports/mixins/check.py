from gn_modulator import SchemaMethods
from pypnnomenclature.repository import get_nomenclature_list

from .utils import ImportMixinUtils


class ImportMixinCheck(ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    Vérification des données
    """

    def process_step_pre_check(self):
        """
        Verfication des données apres l'insertion des données
        (et de la phase de mapping si elle a lieu)
        - on vérifie
            - le bon typage des données
            - est ce que les colonnes qui permettre d'assurer l'unicité sont bien présentes
        """

        self.check_uniques()
        self.check_types()

    def process_step_post_check(self):
        """
        Verification des données
        Avant la phase d'insertion des données
        - les champs requis sont ils présents
        - les clé étrangères sont-elles bien résolues
        """

        self.check_required()
        self.check_resolve_keys()

    def check_uniques(self):
        """
        Vérification
        - est ce que les colonnes qui permettre d'assurer l'unicité sont bien présentes
        Ces champs permette la bonne résolution de la clé primaire
        """

        # - sur la table de mapping si elle existe
        # - ou sur la table des données
        table_test = self.tables["mapping"]

        # liste des colonnes de la table testée
        columns = self.get_table_columns(table_test)

        # récupération de la liste des champs d'unicité
        unique = self.sm().unique()

        # recherche des champs manquant
        missing_unique = [key for key in unique if key not in columns]

        # ajout d'une erreur si un champs d'unicité est manquant
        if missing_unique:
            self.add_error(
                error_code="ERR_IMPORT_MISSING_UNIQUE",
                error_msg=f"Import {self.schema_code}, il manque des champs d'unicité : {', '.join(missing_unique) }",
            )

    def check_types(self):
        """
        Verification
        - si le format données d'entrée correspondent bien au type destinaire
        - pour les nombres, les dates, les geometries, les uuid etc..
        """

        # - sur la table de mapping si elle existe
        # - ou sur la table des données
        table_test = self.tables["mapping"]

        # pour chaque colonne de la table qui est aussi dans la table destinataire
        for key in filter(
            lambda x: self.Model().is_column(x) and not self.Model().is_foreign_key(x),
            self.get_table_columns(table_test),
        ):
            # récupération du type SQL de la colonne
            sql_type = self.Model().sql_type(key)

            # la fonction gn_modulator.check_value_for_type
            # renvoie faux pour les colonnes ou le format ne correspond pas
            # si par exemple on a xxxx-xx-xx pour une date
            #
            # La requete suivante permet de récupérer les lignes en erreur (référencées par id_import)
            # pour une colonne donnée
            sql_check_type_for_column = f"""
            SELECT
              COUNT(*),
              ARRAY_AGG(id_import),
              ARRAY_AGG({key})
            FROM {table_test}
            WHERE NOT (
                {key} is NULL
                OR
                gn_modulator.check_value_for_type('{sql_type}', {key}::VARCHAR)
            )
            GROUP BY id_import
            ORDER BY id_import
        """
            res = SchemaMethods.c_sql_exec_txt(sql_check_type_for_column).fetchone()

            # s'il n'y a pas d'erreur on passe à la colonne suivante
            if res is None:
                continue

            # Ajout d'une erreur qui référence les lignes concernées
            nb_lines = res[0]
            lines = res[1]
            error_values = res[2]
            # str_lines = lines and ", ".join(map(lambda x: str(x), lines)) or ""
            if nb_lines == 0:
                continue
            self.add_error(
                error_code="ERR_IMPORT_INVALID_VALUE_FOR_TYPE",
                key=key,
                lines=lines,
                error_values=error_values,
                error_msg=f"Valeurs invalides pour `{key}` ({sql_type}).",
            )

    def check_required(self):
        """
        Verification que les champs obligatoire sont bien présent
        Les champs obligatoires sont les champs 'not null' et ne possédant pas de valeur par défaut
        """

        # on vérifie sur la table 'raw'
        raw_table = self.tables["raw"]

        # Pour toutes les colonnes obligatoires de la table 'raw'
        for key in self.get_table_columns(raw_table):
            if not self.sm().is_required(key):
                continue

            # requête pour repérer les lignes ayant des éléments à NULL
            # pour cette colonne
            txt_check_required = f"""
SELECT
    COUNT(*), ARRAY_AGG(id_import)
    FROM {raw_table}
    WHERE {key} is NULL
"""

            res = SchemaMethods.c_sql_exec_txt(txt_check_required).fetchone()
            nb_lines = res[0]
            lines = res[1]

            # s'il n'y pas de résultat
            # on passe à la colonne suivante
            if nb_lines == 0:
                continue

            # sinon on ajoute une erreur qui référence les lignes concernées
            self.add_error(
                error_code="ERR_IMPORT_REQUIRED",
                key=key,
                lines=lines,
                error_msg=f"Champs {key} obligatoire et de valeur nulle",
            )

        return

    def check_resolve_keys(self):
        """
        Vérification de la bonne réslution des clé étrangères
        - pour une colonne représentant une clé étrangère
          - si une ligne de la table 'raw' est non nulle
          - et que la ligne correspondant dans la table 'process' est nulle
          - alors on ajoute une erreur de non résolution de la clé étrangère
        """

        # on va comparer les lignes des tables 'raw' et 'process'
        raw_table = self.tables["raw"]
        process_table = self.tables["process"]

        # pour toutes les clés représentant un clé étrangère
        for key in self.get_table_columns(raw_table):
            if key in self.options.get("skip_check_on", []) or not (
                self.Model().is_foreign_key(key) and "." not in key
            ):
                continue

            # requête sql pour lister les 'id_import' des lignes qui sont
            # - non nulles dans 'raw'
            # - et nulles dans 'process
            txt_check_resolve_keys = f"""
SELECT COUNT(*), ARRAY_AGG(r.id_import), ARRAY_AGG(r.{key})
FROM {raw_table} r
JOIN {process_table} p
    ON r.id_import = p.id_import
WHERE
    p.{key} is NULL and r.{key} is NOT NULL
            """

            res = SchemaMethods.c_sql_exec_txt(txt_check_resolve_keys).fetchone()
            nb_lines = res[0]
            lines = res[1]
            error_values = res[2]

            # s'il n'y a pas de résultat, on passe à la colonne suivante
            if nb_lines == 0:
                continue

            # sinon on ajoute une erreur référençant les lignes concernée

            valid_values = None

            # Dans le cas des nomenclatures on peut faire remonter les valeurs possible ??
            code_type = self.Model().get_nomenclature_type(key)
            if code_type:
                valid_values = list(
                    map(
                        lambda x: {
                            "cd_nomenclature": x["cd_nomenclature"],
                            "label_fr": x["label_fr"],
                        },
                        get_nomenclature_list(code_type=code_type)["values"],
                    )
                )
            self.add_error(
                error_code="ERR_IMPORT_UNRESOLVED",
                key=key,
                lines=lines,
                error_msg=f"Clé étrangère '{key}' non résolue ",
                valid_values=valid_values,
                error_values=error_values,
            )
