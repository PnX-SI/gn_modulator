from gn_modulator import SchemaMethods
from .utils import ImportMixinUtils


class ImportMixinCount(ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    Comptage des différentes tables liées à l'import
    """

    def process_count(self):
        """
        Methode pour compter
        - le nombre de lignes insérées
        - le nombre de lignes mise à jour
        - le nombre de lignes inchangées (process - (insert + update) )
        """

        self.count_insert()
        self.count_update()

        if self.errors:
            return

        self.res["nb_unchanged"] = (
            self.res["nb_process"] - self.res["nb_insert"] - self.res["nb_update"]
        )

    def count_insert(self):
        """
        methode pour compter le nombre de ligne insérée
        - une ligne de la table 'process'
        - dont la clé primaire n'est pas résolue (cad à NULL)
        """

        # depuis la table process
        from_table = self.tables["process"]

        sm = SchemaMethods(self.schema_code)

        # requete pour compter les lignes dont la clé primaire est à null
        self.sql[
            "nb_insert"
        ] = f"SELECT COUNT(*) FROM {from_table} WHERE {sm.pk_field_name()} IS NULL"

        try:
            self.res["nb_insert"] = SchemaMethods.c_sql_exec_txt(self.sql["nb_insert"]).scalar()
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_INSERT_COUNT",
                msg=f"Erreur lors du comptage du nombre d'insert: {str(e)}",
            )
            return

    def count_update(self):
        """
        methode pour compter le nombre de ligne mise à jour
        - un ligne mise à jour est une ligne de la table 'process'
          - dont la clé primaire (pk) est résolue
          - et dont au moins une des colonnes (autre que pk) différe de la table destinaire
          - on teste aussi les relation n-n (en comparent des liste de clé étrangères)

        voir 'sql_nb_update' pour la requete
        """

        self.sql["nb_update"] = self.sql_nb_update()
        try:
            self.res["nb_update"] = SchemaMethods.c_sql_exec_txt(self.sql["nb_update"]).scalar()
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_UPDATE_COUNT",
                msg=f"Erreur lors du comptage du nombre d'update: {str(e)}",
            )
        return

    def sql_nb_update(self):
        """
        requete sql pour compter le nombre de ligne mise à jour
        """
        sm = SchemaMethods(self.schema_code)

        # toutes les colonnes de la table 'raw' sauf la clé primaire
        columns = list(
            filter(
                lambda x: sm.has_property(x) and not sm.is_primary_key(x),
                self.get_table_columns(self.tables["raw"]),
            )
        )

        # condition pour la mise à jour d'une ligne
        # on regarde si la valeur change entre la table 'process' et la table destinaire
        # pour les relations n-n, on compare des liste d'entiers
        update_conditions_columns = list(
            map(lambda x: self.update_count_condition_column(x), columns)
        )

        # pour les relations n-n, ajout de with et join dans la requete
        # les sous requete permettre d'agreger les clé étrangère dans des liste
        # pour pouvoir comparer les valeurs des données et les valeurs existantes
        relations_nn = list(
            filter(
                lambda x: sm.is_relation_n_n(x),
                columns,
            )
        )
        withs_rel = list(map(lambda x: self.update_count_with_rel(x), relations_nn))
        joins_rel = list(map(lambda x: self.update_count_join_rel(x), relations_nn))

        # condition de MAJ en txt
        txt_update_conditions = "" + "\n    OR ".join(update_conditions_columns)

        withs_rel_txt = ""
        joins_rel_txt = ""

        # s'il y a des relations n-n
        # texte pour les with et join associés à ces relations
        if len(withs_rel):
            withs_rel_txt = "    WITH " + "\n,".join(withs_rel)
            joins_rel_txt = "\n".join(joins_rel)

        # requete pour compter le nombre de ligne à mettre à jour
        return f"""{withs_rel_txt}
    SELECT
        COUNT(*)
    FROM {sm.sql_schema_dot_table()} t
    JOIN {self.tables['process']} a
        ON a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
{joins_rel_txt}
    WHERE {txt_update_conditions}
;
"""

    def update_count_condition_column(self, key):
        """
        renvoie le texte sql pour comparer pour une colonne données (key)
        - la valeur de la table process
        - la valeur de la table destinataires
        - pour les relation n-n, on utilise des sous requete pour agréger et comparer des listes d'entiers
        """
        sm = SchemaMethods(self.schema_code)
        if sm.is_relation_n_n(key):
            return f"""process_{key}.a IS DISTINCT FROM cor_{key}.a"""

        return f"(t.{key}::TEXT IS DISTINCT FROM a.{key}::TEXT)"

    def update_count_with_rel(self, key):
        """
        texte utilisé pour faire des sous-requete pour les relations n-n
        """

        sm = SchemaMethods(self.schema_code)
        rel = SchemaMethods(sm.property(key)["schema_code"])

        # clé primaire
        pk = sm.pk_field_name()

        # clé primaire de la relation
        rel_pk = rel.pk_field_name()

        # table de correlation
        cor_table = sm.property(key)["schema_dot_table"]

        # sous requete pour agréger les clé dans une liste
        # cor_{key} : pour les clé existantes (cor_table)
        # process_{key} : pour le données du fichier à importers
        #  (table self.tables['relations'][key]['process'], voir ./relation.py)
        return f"""process_{key} AS (
        SELECT
            {pk},
            ARRAY_AGG({rel_pk}) AS a
            FROM {self.tables['relations'][key]['process']}
            GROUP BY {pk}
    ), cor_{key} AS (
        SELECT
            {pk},
            ARRAY_AGG({rel_pk}) AS a
            FROM {cor_table}
            GROUP BY {pk}
    )"""

    def update_count_join_rel(self, key):
        """
        texte sql pour les jointures des sous-requêtes de la fonctions
        pour les tables
            - process_{key}: données à importer
            - cor_{key}: données existantes
        """

        sm = SchemaMethods(self.schema_code)
        pk = sm.pk_field_name()

        return f"""    LEFT JOIN process_{key}
        ON process_{key}.{pk} = t.{pk}
    LEFT JOIN cor_{key}
        ON cor_{key}.{pk} = t.{pk}"""
