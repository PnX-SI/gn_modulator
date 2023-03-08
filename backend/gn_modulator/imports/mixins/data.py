from pathlib import Path
from .utils import ImportMixinUtils
from gn_modulator.schema import SchemaMethods
from geonature.utils.env import db


class ImportMixinData(ImportMixinUtils):
    def process_data_table(self):
        if self.tables.get("data"):
            return

        self.tables["data"] = self.table_name("data")

        if Path(self.data_file_path).suffix == ".csv":
            self.data_type = "csv"
            self.import_csv_file(self.tables["data"])

        # TODO traiter autres types de fichier

        else:
            self.add_error(
                code="ERR_IMPORT_DATA_FILE_TYPE_NOT_FOUND",
                msg=f"Le type du fichier d'import {self.data_file_path} n'est pas traité",
            )
            return

        self.count_and_check_table("data", self.tables["data"])

    def import_csv_file(self, dest_table):
        if not Path(self.data_file_path).exists():
            self.add_error(
                code="ERR_IMPORT_DATA_FILE_NOT_FOUND",
                msg=f"Le fichier d'import {self.data_file_path} n'existe pas",
            )
            return

        with open(self.data_file_path, "r") as f:
            # on récupère la premiere ligne du csv pour avoir le nom des colonnes
            first_line = f.readline()

            self.csv_delimiter = ";" if ";" in first_line else "," if "," in first_line else None

            if self.csv_delimiter is None:
                self.add_error(
                    code="ERR_IMPORT_CSV_FILE_DELIMITER_NOT_FOUND",
                    msg=f"Pas de séparateur trouvé pour le fichier csv {self.data_file_path}",
                )
                return

            import_table_columns = first_line.replace("\n", "").split(self.csv_delimiter)

            # creation de la table temporaire
            self.sql["data_table"] = self.sql_create_data_table(
                self.tables["data"], import_table_columns
            )
            try:
                SchemaMethods.c_sql_exec_txt(self.sql["data_table"])
            except Exception as e:
                self.add_error(
                    code="ERR_IMPORT_DATA_CREATE_TABLE",
                    msg=f"Erreur durant la création de la table des données: {str(e)}",
                )
                return
            # on copie les données dans la table temporaire

            # pour faire marcher les tests pytest on passe par un insert
            # TODO faire marche copy_expert avec pytest
            #       manière de récupérer cursor ?
            if self._insert_data:
                self.insert_csv_data(f, dest_table, import_table_columns)
            else:
                self.copy_csv_data(f, dest_table, import_table_columns)

    def copy_csv_data(self, f, dest_table, table_columns):
        columns_fields = ", ".join(table_columns)
        self.sql[
            "data_copy_csv"
        ] = f"""COPY {dest_table}({columns_fields}) FROM STDIN DELIMITER '{self.csv_delimiter}' QUOTE '"' CSV """
        try:
            cursor = db.session.connection().connection.cursor()
            cursor.copy_expert(sql=self.sql["data_copy_csv"], file=f)
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_DATA_COPY",
                msg=f"Erreur lors de la copie des données csv : {str(e)}",
            )
            return

    def insert_csv_data(self, f, dest_table, table_columns):
        sql_columns_fields = ", ".join(table_columns)

        values = ""
        for line in f:
            data = "', '".join((line.replace('"', "").replace("\n", "").split(self.csv_delimiter)))
            values += f"('{data}'),"
        if not values:
            return

        values = values[:-1]
        self.sql[
            "data_insert"
        ] = f"INSERT INTO {dest_table} ({sql_columns_fields}) VALUES {values}"
        try:
            SchemaMethods.c_sql_exec_txt(self.sql["data_insert"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_DATA_INSERT",
                msg=f"Erreur lors de l'insertion des données csv : {str(e)}",
            )
            return

    def sql_create_data_table(self, dest_table, table_columns):
        """
        requete de creation d'une table temporaire pour import csv
        tout les champs sont en varchar
        """

        columns_sql = "\n    ".join(map(lambda x: f"{x} VARCHAR,", table_columns))
        pk_constraint_name = f"pk_{'_'.join(dest_table.split('.'))}_id_import"

        txt = f"""CREATE TABLE IF NOT EXISTS {dest_table} (
    id_import SERIAL NOT NULL,
    {columns_sql}
    CONSTRAINT {pk_constraint_name} PRIMARY KEY (id_import)
);"""
        return txt
