from .utils import ImportMixinUtils
from .raw import ImportMixinRaw
from .insert import ImportMixinInsert
from .process import ImportMixinProcess
from gn_modulator import SchemaMethods


class ImportMixinRelation(ImportMixinInsert, ImportMixinProcess, ImportMixinRaw, ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    gestion des relations n-n
    """

    def get_n_n_relations(self):
        """
        renvoie la liste des colonnes d'une table associés à une relations n-n
        """
        sm = SchemaMethods(self.schema_code)
        return list(
            filter(
                lambda x: sm.is_relation_n_n(x),
                self.get_table_columns(self.tables["raw"]),
            )
        )

    def process_relations_view(self):
        """
        crée les vue de process pour toutes les relation n-n
        """

        # stockage des table et du sql pour les relations
        self.sql["relations"] = self.sql.get("relations") or {}
        self.tables["relations"] = self.tables.get("relations") or {}

        # boucle sur les relations n-n
        for key in self.get_n_n_relations():
            self.process_relation_views(key)

    def process_relations_data(self):
        """
        insert les données pour toutes les relation n-n
        """

        # boucle sur les relations n-n
        for key in self.get_n_n_relations():
            self.process_relation_data(key)

    def process_relation_views(self, key):
        """
        creation des vues pour la relation n-n référencée par key
        """

        # stockage des tables et du sql pour la relation n-n <key>
        sql_rel = self.sql["relations"][key] = {}
        tables_rel = self.tables["relations"][key] = {}

        # nommage de la vue process de la relation n-n key
        tables_rel["process"] = self.table_name("process", key)

        # creation de la vue de process
        sql_rel["process_view"] = self.sql_process_view(
            self.tables["raw"], tables_rel["process"], key_nn=key
        )

        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["process_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_CREATE_PROCESS_VIEW",
                msg=f"Erreur dans la creation de la vue 'process' pour {key}: {str(e)}",
                key=key,
            )
            return

    def process_relation_data(self, key):
        """
        Gestion des données pour une relation n-n associée à key
        """

        sm = SchemaMethods(self.schema_code)

        # tables et code sql associé à n-n key
        tables_rel = self.tables["relations"][key]
        sql_rel = self.tables["relations"][key]

        property = sm.property(key)

        # table de corrélation
        cor_table = property["schema_dot_table"]

        rel = SchemaMethods(property["schema_code"])

        # - script de suppression des données
        #   dans la table de correlation
        #   on supprime toutes les données associé aux lignes d'import
        sql_rel[
            "delete"
        ] = f"""
DELETE FROM {cor_table} t
    USING {tables_rel['process']} j
    WHERE t.{sm.pk_field_name()} = j.{sm.pk_field_name()};
"""
        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["delete"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_DELETE",
                msg=f"Erreur dans la suppression pour la relation {key}: {str(e)}",
            )
            return

        # - script d'insertion des données
        #   dans la table de correlation
        #   on ajoute toutes les données associé aux lignes d'import
        sql_rel["insert"] = self.sql_insert(
            tables_rel["process"],
            keys=[sm.pk_field_name(), rel.pk_field_name()],
            dest_table=cor_table,
        )
        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["insert"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_RELATION_INSERT",
                msg=f"Erreur dans l'insertion pour la relation {key}: {str(e)}",
            )
            return
