import re
from pathlib import Path
from gn_modulator.utils.commons import getAttr
from .utils import ImportMixinUtils


class ImportMixinLog(ImportMixinUtils):
    def pretty_errors_txt(self):
        txt = ""
        for error in self.errors:
            relation_key = f"({self.relation_key}) " if self.relation_key else ""
            txt += f"- {relation_key}{error['error_code']} :\n"
            txt += f"    {error['error_msg']}"

        for import_relation in self.imports_1_n:
            txt += import_relation.pretty_errors_txt()

        return txt

    def pretty_infos_txt(self):
        """
        Affiche des informations de l'import
        Pour les imports en ligne de commande
        """

        txt = ""
        if self.res.get("nb_data") is not None:
            txt += f"\n-- import csv file {Path(self.data_file_path).name}"
            txt += f"   {self.res.get('nb_data')} lignes\n\n"
        txt += f"   - {self.schema_code} {self.relation_key or ''}\n"
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

        for import_relation in self.imports_1_n:
            txt += import_relation.pretty_infos_txt()

        return txt

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

        txt = f"-- Log Import {replace_id if replace_id else self.id_import}\n"
        txt += f"-- - schema_code: {self.schema_code}\n"

        # explication des tables
        txt += self.txt_tables()

        # gestion du fichier à importer
        txt += self.txt_sql("Creation de la table des données", "data_table")
        txt += self.txt_sql("Copie des données", "data_copy_csv")
        txt += self.txt_sql("Insertion des données", "data_insert")
        txt += self.txt_sql("Creation de la vue de données", "data_view")

        # mapping
        txt += self.txt_sql("Mapping", "mapping_view")

        # raw
        txt += self.txt_sql("Typage (raw)", "raw_view")

        # process
        txt += self.txt_sql("Vue d'import", "import_view")

        # comptage
        txt += self.txt_sql("Comptage insert", "nb_insert")
        txt += self.txt_sql("Comptage update", "nb_update")

        # insert
        txt += self.txt_sql("Insertion des données", "insert")

        # update
        txt += self.txt_sql("Mise à jour des données", "update")

        # relations
        if self.sql["relations"]:
            txt += f"-- - Traitement relations n-n\n\n"

        for key in self.sql["relations"]:
            txt += f"--   - {key}\n"
            txt += self.txt_sql("    - import", f"relations.{key}.import_view")
            txt += self.txt_sql("    - suppression", f"relations.{key}.delete")
            txt += self.txt_sql("    - insertion", f"relations.{key}.insert")

        for import_rel in self.imports_1_n:
            txt += import_rel.all_sql(replace_id)

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

    def pretty_steps_txt(self):
        txt = ""
        total = 0
        for step in self.import_steps():
            if step not in self.steps:
                continue
            txt += f"- {self.relation_key or ''} {step:20s}: {self.steps[step]['time']:.4f}\n"
            total += self.steps[step]["time"]
        txt += f"\n- {'total':20s}: {total:.4f}\n"

        return txt
