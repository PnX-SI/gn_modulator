from geonature.utils.env import db


class SchemaDataImports:
    @classmethod
    def import_process_data(
        cls, import_number, schema_code, data_file_path, dest_table, insert=False, keep_raw=False
    ):
        """
        cree une vue a partir d'un fichier csv pour pouvoir traiter les données ensuite

        le fichier csv
            separateur : ';'
        créé
            - une table temporaire pour avoir les données du csv en varchar
            - une vue pour passer les champs en '' à NULL
        """

        # cas où la table d'import à été générée lors d'un import d'un import précédent

        if not keep_raw:
            cls.import_csv_file(
                import_number, schema_code, data_file_path, dest_table, insert=insert
            )

        cls.count_and_check_table(import_number, schema_code, dest_table, "data")

        return

    @classmethod
    def import_csv_file(cls, import_number, schema_code, data_file_path, dest_table, insert=False):
        if not data_file_path.exists():
            cls.import_add_error(
                import_number,
                schema_code,
                code="ERR_IMPORT_DATA_FILE_NOT_FOUND",
                msg=f"Le fichier d'import {data_file_path} n'existe pas",
            )
            return

        with open(data_file_path, "r") as f:
            # on récupère la premiere ligne du csv pour avoir le nom des colonnes
            first_line = f.readline()

            delimiter = ";" if ";" in first_line else "," if "," in first_line else None

            import_table_columns = first_line.replace("\n", "").split(delimiter)

            cls.import_set_infos(import_number, schema_code, "delimiter", delimiter)
            cls.import_set_infos(
                import_number, schema_code, "import_table_columns", import_table_columns
            )

            if delimiter is None:
                cls.import_add_error(
                    import_number,
                    schema_code,
                    code="ERR_IMPORT_CSV_FILE_DELIMITER_NOT_FOUND",
                    msg=f"Pas de séparateur trouvé pour le fichier csv {data_file_path}",
                )
                return
            # creation de la table temporaire
            import_txt_create_import_table = cls.import_txt_create_import_table(
                import_number, schema_code, dest_table, import_table_columns
            )
            cls.import_set_infos(
                import_number,
                schema_code,
                "sql.import",
                import_txt_create_import_table,
            )
            cls.c_sql_exec_txt(import_txt_create_import_table)

            # on copie les données dans la table temporaire

            # pour faire marcher les tests pytest on passe par un insert
            # TODO faire marche copy_expert avec pytest
            #       manière de récupérer cursor ?
            if insert:
                cls.import_csv_insert(
                    import_number, schema_code, f, dest_table, import_table_columns, delimiter
                )
            else:
                columns_fields = ", ".join(import_table_columns)
                txt_copy_from_csv = f"""COPY {dest_table}({columns_fields}) FROM STDIN DELIMITER '{delimiter}' QUOTE '"' CSV"""
                cls.import_set_infos(import_number, schema_code, "sql.csv_copy", txt_copy_from_csv)
                cursor = db.session.connection().connection.cursor()
                cursor.copy_expert(sql=txt_copy_from_csv, file=f)

    @classmethod
    def import_csv_insert(
        cls, import_number, schema_code, f, dest_table, table_columns, delimiter
    ):
        sql_columns_fields = ", ".join(table_columns)

        values = ""
        for line in f:
            data = "', '".join((line.replace('"', "").replace("\n", "").split(delimiter)))
            values += f"('{data}'),"
        if not values:
            return

        values = values[:-1]
        txt_insert_csv = f"INSERT INTO {dest_table} ({sql_columns_fields}) VALUES {values}"
        cls.import_set_infos(import_number, schema_code, "sql.csv_insert", txt_insert_csv)
        cls.c_sql_exec_txt(txt_insert_csv)

    @classmethod
    def import_txt_create_import_table(cls, import_number, schema_code, dest_table, table_columns):
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
