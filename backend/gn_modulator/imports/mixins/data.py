from pathlib import Path
from .utils import ImportMixinUtils
from gn_modulator.schema import SchemaMethods
from geonature.utils.env import db
import csv


class ImportMixinData(ImportMixinUtils):
    """
    Classe de mixin destinée à TImport

    Insertion des données fichiers dans une table temporaire
    """

    def process_data_table(self):
        """
        methodes pour insérer les données d'un fichier csv
        dans une table temporaire nommée self.tables['data']
        """

        # si la table existe déjà, on passe
        if self.tables.get("data"):
            return

        # nommage de la table
        self.tables["data"] = self.table_name("data")

        # Traitement des fichiers csv
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

        # comptage du nombre de ligne et verification de l'intégrité de la table
        self.count_and_check_table("data", self.tables["data"])

    def import_csv_file(self, dest_table):
        """
        méthode pour lire les fichiers csv
        et copier (ou insérer) les lignes dans une table
        """

        # test si le fichier existe
        if not Path(self.data_file_path).exists():
            self.add_error(
                code="ERR_IMPORT_DATA_FILE_NOT_FOUND",
                msg=f"Le fichier d'import {self.data_file_path} n'existe pas",
            )
            return

        with open(self.data_file_path, "r") as f:
            # on récupère la premiere ligne du csv (header) pour avoir le nom des colonnes
            first_line = f.readline()

            # Détection automatique du délimiteur
            self.csv_delimiter = ";" if ";" in first_line else "," if "," in first_line else None

            if self.csv_delimiter is None:
                self.add_error(
                    code="ERR_IMPORT_CSV_FILE_DELIMITER_NOT_FOUND",
                    msg=f"Pas de séparateur trouvé pour le fichier csv {self.data_file_path}",
                )
                return

            # liste des colonnes du fichier csv
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
            # cette table contient les données au format texte (varchar)

            # avec l'option "insert_data"
            # on peut choisir de faire une requête d'insertion des données
            if self.options.get("insert_data"):
                self.insert_csv_data(f, dest_table, import_table_columns)

            # sinon on utilise l'instruction copy
            else:
                self.copy_csv_data(f, dest_table, import_table_columns)

            # on met à jour la table pour changer les valeurs '' en NULL
            set_columns_txt = ", ".join("NULLIF({key}, '') AS {key}")

            self.sql[
                "process_data"
            ] = f"""
            UPDATE {dest_table} SET {set_columns_txt};
            """

    def copy_csv_data(self, f, dest_table, table_columns):
        """
        requete sql pour copier les données en utilisant cursor.copy_expert
        """

        # la liste des colonne à copier
        columns_fields = ", ".join(table_columns)

        # instruction de copie des données depuis STDIN
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
        """
        méthode pour insérer les données avec une commande INSERT
        (sert principalement pour les test, COPY est sensé être plus rapide pour les grands fichiers)
        """

        sql_columns_fields = ", ".join(table_columns)

        values = []

        # lecture des données avec csv.reader
        csvreader = csv.reader(f, delimiter=self.csv_delimiter, quotechar='"')

        # creation de VALUES
        for row in csvreader:
            data = ",".join(map(lambda x: f"'{x}'", row))
            values.append(f"({data})")
        if not values:
            return

        # VALUES au format texte
        values_txt = ",\n".join(values)

        # requete d'insertion
        self.sql[
            "data_insert"
        ] = f"INSERT INTO {dest_table} ({sql_columns_fields}) VALUES {values_txt}"
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
        tous les champs sont en varchar
        """

        # déclaration des colonnes de la table
        columns_sql = "\n    ".join(map(lambda x: f"{x} VARCHAR,", table_columns))

        # contrainte de clé primaire pour id_import
        # qui référence les lignes d'import
        pk_constraint_name = f"pk_{'_'.join(dest_table.split('.'))}_id_import"

        # requete de creation de la table
        txt = f"""CREATE TABLE IF NOT EXISTS {dest_table} (
    id_import SERIAL NOT NULL,
    {columns_sql}
    CONSTRAINT {pk_constraint_name} PRIMARY KEY (id_import)
);"""
        return txt
