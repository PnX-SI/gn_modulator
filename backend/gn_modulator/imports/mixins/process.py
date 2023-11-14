from gn_modulator import SchemaMethods
from .utils import ImportMixinUtils
from copy import copy


class ImportMixinProcess(ImportMixinUtils):
    """
        Classe de mixin destinée à TImport

        méthode pour résoudre les clé étrangère (et primaire)

        on passe d'une vue qui contient les clé étrangère sous forme de code
        et l'on essaye de retrouver la valeur de clé étrangère à partir du code

        pour cela, on a besoin de connaitre la liste des champs qui permettent de faire l'unicité
        pour toutes les tables concernées

        quand il y a plusieurs champs d'unicité,

    table                       champs                              exemple

    pr_sipaf.t_passage_faunes   ['uuid_passage_faune']              'ff13308e-f404-4603-a480-e0559dc59baf'
    ref_geo.l_areas :           ['id_type', 'area_code']            'COM|48061' (Florac trois rivières)
    ref_nomenclatures.t_nomenclature ['id_type', 'cd_nomenclature'] 'STADE_VIE|2' (Adulte)

    pour les nomenclatures, on ne renseigne que le code (le type de nomenclature était connu pour une colonne)
    """

    def process_step_import_view(self):
        """
        Création de la vue de process
        """

        # table source : raw
        from_table = self.tables["raw"]

        # table destinataire : process
        dest_table = self.tables["process"] = self.table_name("process")

        # requete de creation de la table process
        self.sql["import_view"] = self.sql_process_import_view(from_table, dest_table)

        try:
            SchemaMethods.c_sql_exec_txt(self.sql["import_view"])
        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_PROCESS_CREATE_VIEW",
                error_msg=f"La vue de process n'a pas pu être créée : {str(e)}",
            )
            return

        # comptage et verification de l'intégrité de la table process
        self.count_and_check_table("process", dest_table)

    def sql_process_import_view(self, from_table, dest_table, relation_key=None):
        """
        requete pour créer la vue process

        """

        # colonnes de la table raw
        from_table_columns = self.get_table_columns(from_table)
        # toutes les colonnes sauf la clé primaires
        columns = (
            [relation_key]
            if relation_key and self.sm().is_relation_n_n(relation_key)
            else list(
                filter(
                    lambda x: (
                        self.sm().is_column(x)
                        and x.startswith(f"{relation_key}.")
                        and not x == self.sm().pk_field_name()
                    ),
                    from_table_columns,
                )
            )
            if relation_key and self.sm().is_relation_1_n(relation_key)
            else list(
                filter(
                    lambda x: (
                        self.sm().is_column(x)
                        and "." not in x
                        and not x == self.sm().pk_field_name()
                    ),
                    from_table_columns,
                )
            )
        )

        # colonnes de la table process
        v_columns = []

        # jointures pour les clé étrangères
        v_joins = []

        # clés résolues
        # - pour réutiliser les jointures si besoin
        solved_keys = {}

        # pour toutes les colonnes (sauf clé primaire)
        for index, key in enumerate(columns):
            # - txt_column: colonne dans la vue de process
            # - v_join: jointures pour les clé étrangère ou les relations n-n
            txt_column, v_join = self.process_column_import_view(index, key)

            # pour solved_keys on ne garde que la column pas l'alias
            # - 'j_1.id_truc AS id_machin' -> 'j_1.id_truc'
            solved_keys[key] = txt_column.split(" AS")[0]

            v_columns.append(txt_column)
            v_joins += v_join

        # résolution de la clé primaire
        # - on peut réutiliser au besoin les clé étrangère déjà résoles
        #   avec solved_keys
        txt_pk_column, v_join = self.resolve_key(
            self.schema_code,
            self.sm().pk_field_name(),
            alias_join_base="j_pk",
            solved_keys=solved_keys,
        )
        v_columns.append(txt_pk_column)
        v_joins += v_join

        # text pour les colonnes et les jointures
        txt_columns = ",\n    ".join(v_columns)
        txt_joins = "\n".join(v_joins)

        group_bys = []

        # Gestion du numérisateur
        # - pour l'insert se sera l'utilisateur courrant (self.id_digitiser)
        # - pour l'update se sera l'utilisateur courrant si la ligne n'a pas de numérisateur
        txt_id_digitiser = ""

        if self.id_digitiser and self.id_digitiser_key():
            group_bys.append(self.id_digitiser_key())
            txt_id_digitiser = f"{self.id_digitiser} AS {self.id_digitiser_key()},\n"

        group_bys.extend(v_columns)

        txt_group_by = ", ".join(map(lambda x: x.split(" AS ")[0], group_bys))
        # paramètres pour la création des vues
        view_params = {
            "dest_table": dest_table,
            "from_table": from_table,
            "pk_field_name": self.sm().pk_field_name(),
            "relation_key": relation_key,
            "txt_id_digitiser": txt_id_digitiser,
            "txt_columns": txt_columns,
            "txt_group_by": txt_group_by,
            "txt_joins": txt_joins,
            "dest_table": dest_table,
        }

        # vue process pour les relations
        if relation_key and self.sm().is_relation_n_n(relation_key):
            return self.import_view_txt_nn(view_params)

        # vue process
        return self.import_view_txt(view_params)

    def import_view_txt_nn(self, view_params):
        """
        vue 'process' pour les relations n-n
        """
        return f"""DROP VIEW IF EXISTS {view_params['dest_table']} CASCADE;
CREATE VIEW {view_params['dest_table']} AS
WITH unnest_{view_params['relation_key']} AS (
    SELECT
        id_import,
        {view_params['pk_field_name']},
        TRIM(UNNEST(STRING_TO_ARRAY({view_params['relation_key']}, ','))) AS {view_params['relation_key']}
        FROM {view_params['from_table']}
), remove_doublons AS (
    SELECT min(id_import) as id_import
    FROM {view_params['from_table']}
    GROUP BY {view_params['pk_field_name']}
)
SELECT
    t.id_import,
    {view_params['txt_columns']}
FROM unnest_{view_params['relation_key']} AS t
JOIN remove_doublons r ON r.id_import = t.id_import
{view_params['txt_joins']};
"""

    def import_view_txt(self, view_params):
        """
        vue 'process' pour la table destinataire
        """
        return f"""DROP VIEW IF EXISTS {view_params['dest_table']} CASCADE;
CREATE VIEW {view_params['dest_table']} AS
SELECT
    min(id_import) AS id_import,
    {view_params['txt_id_digitiser']}{view_params['txt_columns']}
FROM {view_params['from_table']} t
{view_params['txt_joins']}
GROUP BY {view_params['txt_group_by']}
;
"""

    def resolve_key(
        self, schema_code, key, index=None, alias_main="t", alias_join_base="j", solved_keys={}
    ):
        """
        resolution des clés étrangères

        entrée
        - schema_code : reference table associée à la clé étrangère
        - key: colonne clé étrangère à résoudre
        - index: index pour numéroter les jointures

        - alias_join_base: nommage de la table de jointure
            {alias_join_base}_{index}
            {alias_join_base} si index is None

        - alais_main: alias pour la table avec laquel on fait la conditin de jointure
            t par defaut (table 'raw')
            j_1 si recursif

        - solved_keys: clé déjà resolues (pour la clé primaire)

        renvoie tuple txt_column, v_join
        - txt_column : le champs de la colonne qui doit contenir la clé
        - v_join : la ou les jointures nécessaire pour résoudre la clé

        """
        sm = SchemaMethods(schema_code)

        # alias pour la jointure associé à la clé étrangère 'key'
        # j_1, j_{index}, j_1_2
        # j_pk pour la clé primaire
        alias_join = alias_join_base if index is None else f"{alias_join_base}_{index}"

        # on renvoie la clé primaire de la table de jointure
        txt_column = f"{alias_join}.{sm.pk_field_name()}"

        # calcul des jointures
        unique = sm.unique()
        v_join = []

        # couf pour permttre de faire les liens entre les join quand il y en a plusieurs
        link_joins = {}

        # boucle sur les champs d'unicité
        for index_unique, k_unique in enumerate(unique):
            # clé de jointure de la table de base correspondant à k_unique
            var_key = self.var_key(
                schema_code, key, k_unique, index_unique, link_joins, alias_main
            )

            # si le champs d'unicité est lui meme une clé étrangère
            if sm.property(k_unique).get("foreign_key"):
                # si elle a déjà été résolue dans solved_keys
                if k_unique in solved_keys:
                    link_joins[k_unique] = solved_keys[k_unique]

                # sinon on la calcule avec resolve_key
                else:
                    rel = SchemaMethods(sm.property(k_unique)["schema_code"])
                    txt_column_join, v_join_inter = self.resolve_key(
                        rel.schema_code(),
                        var_key,
                        index=index_unique,
                        alias_main=alias_join,
                        alias_join_base=alias_join,
                    )
                    # ajout des jointures
                    v_join += v_join_inter

                    # clarifier link oin
                    link_joins[k_unique] = f"{alias_join}_{index_unique}.{rel.pk_field_name()}"

        # conditions de jointures
        v_join_on = []

        # boucles sur les champs d'unicité
        for index_unique, k_unique in enumerate(unique):
            # clé de jointure de la table de base correspondant à k_unique
            var_key = self.var_key(
                schema_code, key, k_unique, index_unique, link_joins, alias_main
            )

            k_unique_type = sm.property(k_unique)["type"]
            cast = ""

            # ????????
            # t correspond à la table raw, ou les champs à résoudre sont très certainement en varchar ?????
            # ????????
            if var_key.startswith("t."):
                cast = (
                    "::UUID"
                    if k_unique_type == "uuid"
                    else "::INTEGER"
                    if k_unique_type == "integer"
                    else ""
                )

            # condition de jointure
            # - "{alias_join}.{k_unique} = {var_key}"
            # - on caste en TEXT pour éviter les pb de comparaison intertype

            # si le champs n'est pas nullable ou obligatoire
            if not sm.is_nullable(k_unique) or sm.is_required(k_unique):
                txt_join_on = f"{alias_join}.{k_unique} = {var_key}{cast}"

            # si le champs peut être NULL
            # - on en tient compte dans la condition de jointure
            else:
                txt_join_on = f"({alias_join}.{k_unique} = {var_key}{cast}\n      OR ({alias_join}.{k_unique} IS NULL AND {var_key} IS NULL))"
            v_join_on.append(txt_join_on)

        # assemblage des conditions de jointure
        txt_joins_on = "\n    AND ".join(v_join_on)

        # texte de la jointure
        txt_join = f"LEFT JOIN {sm.sql_schema_dot_table()} {alias_join}\n    ON {txt_joins_on}"

        # ajout du texte de la jointure à v_join
        v_join.append(txt_join)

        return txt_column, v_join

    def var_key(self, schema_code, key, k_unique, index_unique, link_joins, alias_main):
        """
        clé
        - de la table d'alias 'alias_main'
        - associé à la clé d'unicité k_unique
        - d'index index_unique dans la liste de clés d'unicités
        - pour la résolution de la clé key
        - link_joins ??
        """

        # ??
        if key is None:
            return f"{alias_main}.{k_unique}"

        # ??
        if link_joins.get(k_unique):
            return link_joins[k_unique]

        # ??
        if "." in key:
            return key

        sm = SchemaMethods(schema_code)

        # s'il y a plusieurs clé d'unicité
        # - on s'attend à une chaine de caractere
        #   contenant plusieurs valeurs séparées par des '|'
        #   'val1|val2'
        # -> on va récupérer la valeur correspondant à l'index_unique
        if len(sm.unique()) > 1:
            return f"SPLIT_PART({alias_main}.{key}, '|', { index_unique + 1})"

        # s'il n'y a qu'une seule clé d'unicité,
        # - on renvoie tout simplement
        #   {alias_main}.{key}
        return f"{alias_main}.{key}"

    def process_column_import_view(self, index, key):
        """
        renvoie txt_column, v_join pour une clé donnée (key)
        - si ce n'est pas une clé etrangère ou une relation n-n
          on renvoie le champs tel quel sans jointures
        - sinon on résoud la clé et on renvoie les jointures
        """

        property = self.sm().property(key)

        # dans le cas des clé étrangères ou des relations n-n
        # si ce n'est pas une clé etrangère ou une relation n-n
        # - on renvoie le champs tel quel sans jointures
        if not (property.get("foreign_key") or self.sm().is_relation_n_n(key)):
            return f"t.{key}", []

        # Pour les clé étrangère ou les relations n-n

        # traitement spécial pour les nomenclatures
        if property.get("nomenclature_type"):
            txt_column, v_join = self.resolve_key_nomenclature(
                key, index, property["nomenclature_type"]
            )
        # on essaye de résoudre la clé étrangère
        else:
            txt_column, v_join = self.resolve_key(property["schema_code"], key, index)

        # pour les relations n-n
        # - on suppose que la clé sera toujours
        #   la clé primaire de la table associée par correlation
        # - TODO sinon à rendre paramétrable
        if self.sm().is_relation_n_n(key):
            rel = SchemaMethods(self.sm().property(key)["schema_code"])
            txt_column = f"{txt_column.split('.')[0]}.{rel.pk_field_name()}"

        # les clé étrangères
        else:
            alias_key = key.split(".")[-1]
            txt_column = f"{txt_column} AS {alias_key}"

        return txt_column, v_join

    def resolve_key_nomenclature(self, key, index, nomenclature_type):
        """
        resolution d'une clé de type nomenclature
        - pour simplifier les fichiers d'import
          on choisit de n'utiliser seulement les codes de nomenclature
        - le type de nomenclature est récupéré depuis la configuration
          on utilise alors la fonction ref_nomenclatures.get_id_nomenclature_type
          pour récupéré le type

          TODO à rendre paramétrable ??
        """

        alias_join = f"j_{index}"
        table = SchemaMethods("ref_nom.nomenclature").sql_schema_dot_table()
        joins_on = [
            f"j_{index}.cd_nomenclature = t.{key}",
            f"j_{index}.id_type = ref_nomenclatures.get_id_nomenclature_type('{nomenclature_type}')",
        ]
        txt_join_on = "\n      AND ".join(joins_on)
        txt_join = f"LEFT JOIN {table} {alias_join} \n    ON {txt_join_on}"
        v_join = [txt_join]
        txt_column = f"{alias_join}.id_nomenclature"
        return txt_column, v_join
