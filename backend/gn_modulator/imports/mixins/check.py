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

        self.check_unique_missing()
        self.check_unique_doublons()
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

    def check_unique_doublons(self):
        table_test = self.tables["mapping"]
        unique = self.sm().unique()
        group_by_columns = ", ".join(
            filter(
                lambda x: self.Model().is_column(x) and "." not in x,
                self.get_table_columns(table_test),
            )
        )
        unique_columns = ", ".join(unique)

        req_check_doublons_unique = f"""
        WITH pre AS (
            SELECT {unique_columns}, ARRAY_AGG(id_import) AS id_import
            FROM {table_test}
            GROUP BY {group_by_columns}
        )
        SELECT COUNT(*), ARRAY_AGG(pre.id_import), CONCAT({unique_columns}) AS is_import
        FROM pre
        GROUP BY {unique_columns}
        HAVING COUNT(*) > 1
        """

        qres = SchemaMethods.c_sql_exec_txt(req_check_doublons_unique)
        res = []
        for r in qres:
            rr = {"count": r[0], "lines": [xx for x in r[1] for xx in x], "value": r[2]}
            res.append(rr)

        if res:
            # TODO ajouter lines
            self.add_error(
                error_code="ERR_IMPORT_UNIQUE_DOUBLON",
                error_msg=f"Doublons trouvés pour les champs d'unicités {unique_columns}",
            )

    def check_unique_missing(self):
        """
        Vérification
        - est ce que les colonnes qui permettre d'assurer l'unicité sont bien présentes
        Ces champs permette la bonne résolution de la clé primaire
        - existence de doublons pour les champs d'unicité ?
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
                error_msg=f"Champs d'unicité non présents : {', '.join(missing_unique) }",
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
            clean_key = self.clean_column_name(key)

            # la fonction gn_modulator.check_value_for_type
            # renvoie faux pour les colonnes ou le format ne correspond pas
            # si par exemple on a xxxx-xx-xx pour une date
            #
            # La requete suivante permet de récupérer les lignes en erreur (référencées par id_import)
            # pour une colonne donnée
            sql_check_type_for_column = f"""
            SELECT
              COUNT(*) as nb_lines,
              ARRAY_AGG(id_import) as lines,
              {clean_key} AS value
            FROM {table_test}
            WHERE NOT (
                {clean_key} is NULL
                OR
                gn_modulator.check_value_for_type('{sql_type}', {clean_key}::VARCHAR)
            )
            GROUP BY {clean_key}
            ORDER BY COUNT(*) DESC
        """
            res = SchemaMethods.c_sql_exec_txt(sql_check_type_for_column).fetchall()

            error_infos = []

            # s'il n'y a pas d'erreur on passe à la colonne suivante
            for r in res:
                error_infos.append(
                    {
                        "value": r["value"],
                        "lines": r["lines"][:5],
                        "nb_lines": r["nb_lines"],
                    }
                )

            if not error_infos:
                continue
            self.add_error(
                error_code="ERR_IMPORT_INVALID_VALUE_FOR_TYPE",
                key=key,
                error_infos=error_infos,
                error_msg=f"valeur invalide ({sql_type})",
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

            error_infos = [{"lines": lines[:5], "nb_lines": nb_lines}]

            # sinon on ajoute une erreur qui référence les lignes concernées
            self.add_error(
                error_code="ERR_IMPORT_REQUIRED",
                key=key,
                error_infos=error_infos,
                error_msg=f"champs obligatoire",
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
SELECT
    COUNT(*)  AS nb_lines,
    ARRAY_AGG(r.id_import ORDER BY r.id_import) AS lines,
    r.{key} AS value
FROM {raw_table} r
JOIN {process_table} p
    ON r.id_import = ANY(p.ids_import)
WHERE
    p.{key} is NULL and r.{key} is NOT NULL
GROUP BY r.{key}
ORDER BY count(*) DESC
            """

            res = SchemaMethods.c_sql_exec_txt(txt_check_resolve_keys).fetchall()

            error_infos = []

            for r in res:
                error_infos.append(
                    {"nb_lines": r["nb_lines"], "lines": r["lines"][:5], "value": r["value"]}
                )

            # s'il n'y a pas de résultat, on passe à la colonne suivante
            if len(error_infos) == 0:
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
                error_msg=f"pas de correspondance",
                valid_values=valid_values,
                error_infos=error_infos,
            )
