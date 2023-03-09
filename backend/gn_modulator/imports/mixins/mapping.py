from pathlib import Path
from .utils import ImportMixinUtils
from gn_modulator.schema import SchemaMethods


class ImportMixinMapping(ImportMixinUtils):
    def process_mapping_view(self):
        """
        Application de la vue de mappage à la la table d'import
        """

        if self.mapping_file_path is None:
            return

        self.tables["mapping"] = self.table_name("mapping")

        if not Path(self.mapping_file_path).exists():
            self.add_error(
                code="ERR_IMPORT_MAPPING_FILE_MISSING",
                msg=f"Le fichier de preprocess {self.mapping_file_path} n'existe pas",
            )
            return

        self.sql["mapping_view"] = self.sql_mapping()
        if self.errors:
            return

        try:
            SchemaMethods.c_sql_exec_txt(self.sql["mapping_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_MAPPING_CREATE_VIEW",
                msg=f"La vue de preprocess n'a pas être crée : {str(e)}",
            )
            return

        self.count_and_check_table("mapping", self.tables["mapping"])

    def sql_mapping(self):
        from_table = self.tables["data"]
        dest_table = self.tables["mapping"]

        with open(self.mapping_file_path, "r") as f:
            mapping_select = f.read().upper().replace(";", "").replace("%", "%%")

            forbidden_words = []
            for forbidden_word in [
                "INSERT ",
                "DROP ",
                "DELETE ",
                "UPDATE ",
                "EXECUTE",
                "TRUNCATE",
            ]:
                if forbidden_word in mapping_select:
                    forbidden_words.append(forbidden_word.strip())

            if forbidden_words:
                self.add_error(
                    code="ERR_IMPORT_MAPPING_FORBIDEN_WORD",
                    msg=f"Le fichier de preprocess {self.mapping_file_path} contient le ou les mots interdits {', '.join(forbidden_word)}",
                )

            if ":TABLE_DATA" not in mapping_select:
                self.add_error(
                    code="ERR_IMPORT_MAPPING_MISSING_TABLE",
                    msg="La selection de mapping doit contenir 'FROM :table_data",
                )

            mapping_select = mapping_select.replace(":TABLE_DATA", from_table)

            if "ID_IMPORT" not in mapping_select:
                self.add_error(
                    code="ERR_IMPORT_MAPPING_MISSING_IMPORT",
                    msg=f"La selection de mapping doit contenir le champs id_import dans {self.mapping_file_path}",
                )

            sql_mapping = f"""
DROP VIEW IF EXISTS {dest_table};
CREATE VIEW {dest_table} AS
{mapping_select}
;
            """

            return sql_mapping
