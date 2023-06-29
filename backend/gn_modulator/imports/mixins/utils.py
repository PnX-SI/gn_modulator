import re
from pathlib import Path

from gn_modulator.schema import SchemaMethods
from gn_modulator.utils.env import schema_import
from gn_modulator.utils.commons import getAttr
from gn_modulator import ModuleMethods


class ImportMixinUtils:
    """
    Classe de mixin destinée à TImport

    Fonction utiles utilisées dans les autres fichiers de ce dossier
    """

    # correspondance type schema, type sql
    sql_type_dict = {
        "integer": "INTEGER",
        "boolean": "BOOLEAN",
        "number": "FLOAT",
        "string": "VARCHAR",
        "date": "DATE",
        "datetime": "TIMESTAMP",
        "uuid": "UUID",
        "geometry": "GEOMETRY",
        "json": "JSONB",
    }

    def init_import(self):
        """
        Initialisation de l'import
        """

        # récupération de schema_code à partir de
        #   - schema_code
        #   - (module_code_object_code)
        self.schema_code = self.schema_code or ModuleMethods.schema_code(
            self.module_code, self.object_code
        )
        if not self.schema_code:
            self.add_error(
                error_code="ERR_IMPORT_SCHEMA_CODE_NOT_FOND",
                error_msg=f"Il n'y a pas de schema pour module_code={self.module_code}, object_code={self.object_code}",
            )

        # Creation du schema d'import s'il n'existe pas
        SchemaMethods.c_sql_exec_txt(f"CREATE SCHEMA IF NOT EXISTS {schema_import}")

        # Verification du srid fourni dans les options
        # - on verifie que c'est bien un entier
        # - pour éviter les injections sql
        if self.options.get("srid"):
            try:
                int(self.options.get("srid"))
            except ValueError:
                self.add_error(
                    error_code="ERR_IMPORT_OPTIONS",
                    error_msg=f"Le srid n'est pas valide {self.options.get('srid')}",
                )

    def pretty_infos(self):
        """
        Affiche des informations de l'import
        Pour les imports en ligne de commande
        """
        txt = ""
        if self.res.get("nb_data") is not None:
            txt += f"\n-- import csv file {Path(self.data_file_path).name}"
            txt += f"   {self.res.get('nb_data')} lignes\n\n"
        txt += f"   - {self.schema_code}\n"
        if self.res.get("nb_raw") != self.res.get("nb_process"):
            txt += f"       raw       : {self.res.get('nb_raw'):10d}\n"
        if self.res.get("nb_process"):
            txt += f"       process   : {self.res.get('nb_process'):10d}\n"
        if self.res.get("nb_insert"):
            txt += f"       insert    : {self.res['nb_insert']:10d}\n"
        if self.res.get("nb_update"):
            txt += f"       update    : {self.res['nb_update']:10d}\n"
        if self.res.get("nb_unchanged"):
            txt += f"       unchanged : {self.res['nb_unchanged']:10d}\n"

        return txt

    def count_and_check_table(self, table_type, table_name):
        """
        Commande qui va
          - compter le nombre de lignes dans une table ou vue (créer pour l'import)
          - permet de vérifier l'intégrité de la table/vue
        """

        if self.errors:
            return

        try:
            self.res[f"nb_{table_type}"] = SchemaMethods.c_sql_exec_txt(
                f"SELECT COUNT(*) FROM {table_name}"
            ).scalar()

        except Exception as e:
            self.add_error(
                error_code="ERR_IMPORT_COUNT_VIEW",
                error_msg=f"Erreur avec la table/vue '{table_type}' {table_name}: {str(e)}",
            )
            return

        if self.res[f"nb_{table_type}"] == 0:
            self.add_error(
                error_code="ERR_IMPORT_COUNT_VIEW",
                error_msg=f"Erreur avec la table/vue '{table_type}' {table_name}: il n'y a n'a pas de données",
            )

    def table_name(self, type, key=None):
        """
        nommange de la table
        """

        if type == "data":
            return f"{schema_import}.t_{self.id_import}_{type}"
        else:
            rel = f"_{key}" if key is not None else ""
            return f"{schema_import}.v_{self.id_import}_{type}_{self.schema_code.replace('.', '_')}{rel}"

    def add_error(
        self,
        error_code=None,
        error_msg=None,
        key=None,
        lines=None,
        valid_values=None,
        error_values=None,
    ):
        """
        ajout d'une erreur lorsque qu'elle est rencontrée
        """
        self.errors.append(
            {
                "error_code": error_code,
                "error_msg": error_msg,
                "key": key,
                "lines": lines,
                "valid_values": valid_values,
                "error_values": error_values,
            }
        )
        self.status = "ERROR"

    def get_table_columns(self, table_name):
        """
        récupération des colonnes d'une table
        - avec mise en cache pour éviter de multiplier les requetes
        """
        if not self._columns.get(table_name):
            self._columns[table_name] = SchemaMethods.get_table_columns(table_name)
        return self._columns[table_name]

    def id_digitiser_key(self):
        """
        gestion du numérisateur
        - on regarde si la table destinataire possède un champs nommé
          - id_digitiser
          - ou id_digitizer
        """
        for key in ["id_digitiser", "id_digitizer"]:
            if SchemaMethods(self.schema_code).has_property(key):
                return key

    def log_sql(self, file_path, replace_id=None):
        """
        écrit le sql réalisé pour un import dans un fichier
        """

        with open(file_path, "w") as f:
            f.write(self.all_sql(replace_id))

    def txt_sql(self, txt_comment, key):
        txt = f"-- {txt_comment}\n\n"
        try:
            sql = getAttr(self.sql, key)
        except KeyError:
            return ""
        txt += sql
        txt += "\n\n"
        return txt

    def txt_tables(self):
        txt = "\n-- Tables et vues utlisées pour l'import\n"

        txt += f"-- - data: {self.tables['data']}\n"
        txt += "--    table contenant les données du fichier à importer\n"
        txt += "--\n"

        if self.tables.get("mapping"):
            txt += f"-- - mapping: {self.tables['mapping']}\n"
            txt += "--    vue permettant de faire la corresondance entre\n"
            txt += "--             le fichier source et la table destinataire\n"
            txt += "--\n"

        txt += f"-- - raw: {self.tables['raw']}\n"
        txt += "--    choix des colonnes, typage\n"
        txt += "--\n"

        txt += f"-- - process: {self.tables['process']}\n"
        txt += "--    résolution des clés\n"
        txt += "--\n"

        for key in self.tables["relations"]:
            txt += f"-- - process relation n-n {key}: {self.tables['relations'][key]['process']}\n"

        txt += "\n\n"
        return txt

    def all_sql(self, replace_id=None):
        """
        agrège les requêtes sql utilisée pour l'import
        """

        txt = "-- Log Import {id import}\n"
        txt += f"-- - schema_code: {self.schema_code}\n"

        # explication des tables
        txt += self.txt_tables()

        # gestion du fichier à importer
        txt += self.txt_sql("Creation de la table des données", "data_table")
        txt += self.txt_sql("Copie des données", "data_copy_csv")
        txt += self.txt_sql("Insertion des données", "data_insert")

        # mapping
        txt += self.txt_sql("Mapping", "mapping_view")

        # raw
        txt += self.txt_sql("Typage (raw)", "raw_view")

        # process
        txt += self.txt_sql("Résolution des clés (process)", "process_view")

        # insert
        txt += self.txt_sql("Insertion des données", "insert")

        # update
        txt += self.txt_sql("Mise à jour des données", "update")

        # relations
        for key in self.sql["relations"]:
            txt += f"-- - Traitement relation n-n {key}\n"
            txt += self.txt_sql("    - process", f"relations.{key}.process_view")
            txt += self.txt_sql("    - suppression", f"relations.{key}.delete")
            txt += self.txt_sql("    - suppression", f"relations.{key}.insert")

        if replace_id:
            txt = self.replace_id_in_txt(txt, replace_id)

        return txt

    def replace_id_in_txt(self, txt, replace_id):
        """
        remplace une id_import par replace_id (par ex 'xxx')
        """

        for k in filter(lambda x: x != "relations", self.tables):
            table_name = self.tables[k]
            txt = self.replace_table_name_in_txt(txt, replace_id, table_name)

        for k in self.tables["relations"]:
            table_name = self.tables["relations"][k]["process"]
            txt = self.replace_table_name_in_txt(txt, replace_id, table_name)

        return txt

    def replace_table_name_in_txt(self, txt, replace_id, table_name):
        table_name_r = table_name.replace(str(self.id_import), replace_id)
        return re.sub(table_name, table_name_r, txt)
