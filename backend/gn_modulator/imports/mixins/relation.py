from .utils import ImportMixinUtils
from .raw import ImportMixinRaw
from .insert import ImportMixinInsert
from .process import ImportMixinProcess
from gn_modulator import SchemaMethods


class ImportMixinRelation(ImportMixinInsert, ImportMixinProcess, ImportMixinRaw, ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    gestion des relations n-n et 1-n
    """

    def process_step_relations_view(self):
        """
        crée les vue de process pour toutes les relation n-n
        """

        # stockage des table et du sql pour les relations
        self.sql["relations"] = self.sql.get("relations") or {}
        self.tables["relations"] = self.tables.get("relations") or {}

        # boucle sur les relations n-n
        for relation_key in self.get_n_n_relations():
            self.process_relation_n_n_views(relation_key)

        # boucle sur les relations 1-n
        for relation_key in self.get_1_n_relations():
            self.create_import_1_n(relation_key)

    def get_1_n_relations(self):
        """
        renvoie la liste des relations 1-n associé aux colonnes des données
        """

        relations_1_n = []
        for key in self.get_table_columns(self.tables["data"]):
            if "." not in key:
                continue
            relation_key = key.split(".")[0]
            if (
                self.Model().is_relation_1_n(relation_key)
                and relation_key not in relations_1_n
                and relation_key not in self.sm().attr("meta.import_excluded_fields", [])
            ):
                relations_1_n.append(relation_key)

        return relations_1_n

    def get_n_n_relations(self):
        """
        renvoie la liste des colonnes d'une table associés à une relations n-n
        """

        return list(
            filter(
                lambda x: self.Model().is_relation_n_n(x) and x.count(".") == 0,
                self.get_table_columns(self.tables["raw"]),
            )
        )

    def process_step_relations_data(self):
        """
        insert les données pour toutes les relation n-n
        """

        # boucle sur les relations n-n
        for relation_key in self.get_n_n_relations():
            self.process_relation_n_n_data(relation_key)

        # boucle sur les relations 1-n
        for relation_key in self.get_1_n_relations():
            self.process_relation_1_n_data(relation_key)

    def create_import_1_n(self, relation_key):
        table_rel_data, sql_rel_data = self.process_relation_1_n_data_views(relation_key)

        relation_import = self.__class__(
            schema_code=self.sm().property(relation_key)["schema_code"],
            options={
                "skip_steps": ["update"],
                "target_step": "post_check",
                "skip_check_on": [self.Model().pk_field_name()],
            },
        )
        relation_import.relation_key = relation_key
        relation_import.tables = relation_import.tables or {}
        relation_import.sql = relation_import.sql or {}
        relation_import.tables["data"] = table_rel_data
        relation_import.sql["data_view"] = sql_rel_data
        self.imports_1_n.append(relation_import)
        relation_import.process_import_schema()

    def process_relation_1_n_data(self, relation_key):
        import_relation_key = self.get_import_1_n(relation_key)
        import_relation_key.sql["delete"] = import_relation_key.delete_relation(
            relation_key,
            import_relation_key.tables["process"],
            import_relation_key.Model().sql_schema_dot_table(),
            self.Model().pk_field_name(),
        )
        import_relation_key.options["target_step"] = None
        import_relation_key.process_import_schema()

    def delete_relation(self, relation_key, from_table, dest_table, pk_field_name):
        sql_delete = f"""DELETE FROM {dest_table} t
    USING {from_table} j
    WHERE t.{pk_field_name} = j.{pk_field_name};
"""
        try:
            SchemaMethods.c_sql_exec_txt(sql_delete)
        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_RELATION_DELETE",
                error_msg=f"Erreur dans la suppression pour la relation {relation_key}: {str(e)}",
            )
        return sql_delete

    def get_import_1_n(self, relation_key):
        """
        récupération de l'import associé à la relation 1-n <relation_key>
        """
        import_1_n = None
        for elem in self.imports_1_n:
            if elem.relation_key == relation_key:
                import_1_n = elem
        return import_1_n

    def process_relation_1_n_data_views(self, relation_key):
        # nommage de la vue raw de la relation n-n relation_key
        tables_rel_data = self.table_name("data", relation_key)

        from_table = self.tables["raw"]

        from_table_columns = self.get_table_columns(from_table)
        rel_columns = [
            f'"{x}" AS {x.split(".")[-1]}'
            for x in from_table_columns
            if x.startswith(f"{relation_key}.")
        ]
        txt_rel_columns = ",\n    ".join(rel_columns)

        sql_rel_data = f"""CREATE VIEW {tables_rel_data} AS
SELECT
    id_import,
    {self.Model().pk_field_name()},
    {txt_rel_columns}
    FROM {from_table}
        """

        try:
            SchemaMethods.c_sql_exec_txt(sql_rel_data)
        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_RELATION_CREATE_DATA",
                error_msg=f"Erreur dans la creation de la vue 'data' pour {relation_key}: {str(e)}",
                key=relation_key,
            )
        return tables_rel_data, sql_rel_data

    def process_relation_n_n_views(self, relation_key):
        """
        creation des vues pour la relation référencée par relation_key
        """

        # stockage des tables et du sql pour la relation n-n <relation_key>
        sql_rel = self.sql["relations"][relation_key] = {}
        tables_rel = self.tables["relations"][relation_key] = {}

        # nommage de la vue process de la relation n-n relation_key
        tables_rel["process"] = self.table_name("process", relation_key)

        # creation de la vue de process
        sql_rel["import_view"] = self.sql_process_import_view(
            self.tables["raw"], tables_rel["process"], relation_key=relation_key
        )
        (sql_rel["import_view"])
        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["import_view"])
        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_RELATION_CREATE_IMPORT_VIEW",
                error_msg=f"Erreur dans la creation de la vue 'process' pour {relation_key}: {str(e)}",
                key=relation_key,
            )
            return

    def process_relation_n_n_data(self, relation_key):
        """
        Gestion des données pour une relation associée à relation_key
        """

        # tables et code sql associé à relation_key
        tables_rel = self.tables["relations"][relation_key]
        sql_rel = self.sql["relations"][relation_key]

        # table de corrélation
        relation_Model = self.Model().relation_Model(relation_key)
        dest_table = (
            self.Model().cor_schema_dot_table(relation_key)
            if self.Model().is_relation_n_n(relation_key)
            else relation_Model.sql_schema_dot_table()
        )

        # - script de suppression des données
        #   dans la table de correlation
        #   on supprime toutes les données associé aux lignes d'import
        sql_rel["delete"] = self.delete_relation(
            relation_key, tables_rel["process"], dest_table, self.Model().pk_field_name()
        )

        # - script d'insertion des données
        #   dans la table de correlation
        #   on ajoute toutes les données associé aux lignes d'import
        keys = [self.Model().pk_field_name(), relation_Model.pk_field_name()]

        sql_rel["insert"] = self.sql_insert(
            tables_rel["process"], keys=keys, dest_table=dest_table
        )

        try:
            SchemaMethods.c_sql_exec_txt(sql_rel["insert"])
        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_RELATION_INSERT",
                error_msg=f"Erreur dans l'insertion pour la relation {relation_key}: {str(e)}",
            )
            return
