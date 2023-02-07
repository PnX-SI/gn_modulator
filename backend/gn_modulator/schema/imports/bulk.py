from geonature.utils.env import db
from pathlib import Path
from gn_modulator.definition import DefinitionMethods

schema_import = "gn_modulator_import"


class SchemaBulkImports:
    @classmethod
    def process_import_file(cls, import_code, data_path, verbose=False):
        """
        import_file est le chemin vers un fichier json qui contient
        les différents fichiers à importer
        """

        # data = cls.load_yml_file(import_file_path)
        import_definition = DefinitionMethods.get_definition("import", import_code)
        import_definition_file_path = DefinitionMethods.get_file_path("import", import_code)
        for d in import_definition["items"]:
            data_file_path = Path(data_path) / d["data"] if d.get("data") else Path(data_path)
            pre_process_file_path = (
                Path(import_definition_file_path).parent / d["pre_process"]
                if d.get("pre_process")
                else None
            )
            cls.process_csv_file(
                schema_code=d["schema_code"],
                data_file_path=data_file_path,
                pre_process_file_path=pre_process_file_path,
                keep_raw=d.get("keep_raw"),
                verbose=verbose,
            )

    @classmethod
    def process_csv_file(
        cls,
        schema_code,
        data_file_path,
        pre_process_file_path=None,
        verbose=False,
        keep_raw=False,
    ):
        """
        import de données

        todo tout types de données
        """

        cls.c_sql_exec_txt(f"CREATE SCHEMA IF NOT exists {schema_import}")

        sm = cls(schema_code)
        raw_import_table = f"{schema_import}.tmp_import_{Path(data_file_path).stem}"
        pre_processed_view = f"{schema_import}.v_pre_processed_import_{sm.schema_code('_')}"
        raw_import_view = f"{schema_import}.v_raw_import_{sm.schema_code('_')}"
        processed_import_view = f"{schema_import}.v_processed_import_{sm.schema_code('_')}"

        # 0) clean
        if not keep_raw:
            cls.c_sql_exec_txt(f"DROP TABLE IF EXISTS {raw_import_table} CASCADE")
        else:
            cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {pre_processed_view} CASCADE")
            cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {raw_import_view} CASCADE")

        # 1) csv -> table temporaire
        if not (cls.c_sql_schema_dot_table_exists(raw_import_table) and keep_raw):
            print(f"-- import csv_file {data_file_path.name} into {raw_import_table}")
            cls.bulk_import_process_csv(schema_code, data_file_path, raw_import_table)

        nb_csv = cls.c_sql_exec_txt(f"SELECT COUNT(*) FROM {raw_import_table}").scalar()

        # 2) pre-process
        if pre_process_file_path is not None:
            with open(pre_process_file_path, "r") as f:
                txt_pre_process_raw_import_view = (
                    f.read()
                    .replace(":raw_import_table", raw_import_table)
                    .replace(":pre_processed_import_view", pre_processed_view)
                    .replace("%", "%%")
                )

                verbose and print(txt_pre_process_raw_import_view.replace("%%", "%"))
                cls.c_sql_exec_txt(txt_pre_process_raw_import_view)
                raw_import_table = pre_processed_view

        # table temporaire -> vue brute
        txt_create_raw_import_view = cls.txt_create_raw_import_view(
            schema_code, raw_import_table, raw_import_view
        )
        verbose and print(txt_create_raw_import_view)
        cls.c_sql_exec_txt(txt_create_raw_import_view)
        cls.c_sql_exec_txt(f"SELECT * FROM {raw_import_table} LIMIT 1")
        db.session.commit()

        # 3) vue brute -> vue prête pour l'import avec les clés étrangéres et primaires résolues
        txt_create_processed_import_view = cls.txt_create_processed_import_view(
            schema_code, raw_import_view, processed_import_view
        )
        verbose and print(txt_create_processed_import_view)
        # print(txt_create_processed_import_view)
        cls.c_sql_exec_txt(txt_create_processed_import_view)
        cls.c_sql_exec_txt(f"SELECT * FROM {processed_import_view} LIMIT 1")

        nb_processed = cls.c_sql_exec_txt(f"SELECT COUNT(*) FROM {processed_import_view}").scalar()
        nb_raw = cls.c_sql_exec_txt(f"SELECT COUNT(*) FROM {raw_import_view}").scalar()
        nb_insert = cls.c_sql_exec_txt(
            f"SELECT COUNT(*) FROM {processed_import_view} WHERE {sm.pk_field_name()} IS NULL"
        ).scalar()
        verbose and print(cls.txt_nb_update(schema_code, processed_import_view))
        nb_update = cls.c_sql_exec_txt(
            cls.txt_nb_update(schema_code, processed_import_view)
        ).scalar()
        # nb_schema_avant = cls.c_sql_exec_txt(
        #     f"SELECT COUNT(*) FROM {cls(schema_code).sql_schema_dot_table()}"
        # ).scalar()

        # return
        # 4) INSERT / UPDATE
        # 4-1) INSERT
        txt_import_view_to_insert = cls.txt_import_view_to_insert(
            schema_code, processed_import_view
        )
        verbose and print(txt_import_view_to_insert)
        cls.c_sql_exec_txt(txt_import_view_to_insert)

        # nb_schema_apres = cls.c_sql_exec_txt(
        #     f"SELECT COUNT(*) FROM {cls(schema_code).sql_schema_dot_table()}"
        # ).scalar()

        print(
            f"   - {schema_code} CSV {nb_csv} RAW {nb_raw} PROCESSED {nb_processed} INSERT {nb_insert} UPDATE {nb_update}"
        )

        # 4-2) UPDATE
        if nb_update:
            txt_import_view_to_update = cls.txt_import_view_to_update(
                schema_code, processed_import_view
            )
            verbose and print(txt_import_view_to_update)
            cls.c_sql_exec_txt(txt_import_view_to_update)

        # # 5) process relations ???
        #  ?? au moins n-n
        cls.bulk_import_process_relations(schema_code, raw_import_table, verbose)
        # return "ok"

    @classmethod
    def bulk_import_process_relations(cls, schema_code, raw_import_table, verbose):
        sm = cls(schema_code)

        columns = cls.get_table_columns(raw_import_table)

        for index, column in enumerate(columns):
            if not sm.is_relationship(column.key):
                continue
            property = sm.property(column.key)

            # on commence par les n-n
            if property.get("relation_type") in ("n-n"):
                cls.bulk_import_process_relation_n_n(
                    schema_code, raw_import_table, column.key, verbose
                )

    @classmethod
    def bulk_import_process_relation_n_n(cls, schema_code, raw_import_table, key, verbose):
        sm = cls(schema_code)

        property = sm.property(key)
        cor_table = property["schema_dot_table"]
        rel = cls(property["schema_code"])

        raw_delete_import_view = f"{schema_import}.v_raw_delete_import_{sm.schema_code('_')}_{key}"
        processed_delete_import_view = (
            f"{schema_import}.v_processed_delete_import_{sm.schema_code('_')}_{key}"
        )
        raw_import_view = f"{schema_import}.v_raw_import_{sm.schema_code('_')}_{key}"
        # pre_processed_view = (
        #   f"{schema_import}.v_pre_processed_import_{sm.schema_code('_')}"
        # )
        processed_import_view = f"{schema_import}.v_processed_import_{sm.schema_code('_')}_{key}"

        # 0) clean
        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {processed_import_view}")
        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {raw_import_view}")
        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {processed_delete_import_view}")
        cls.c_sql_exec_txt(f"DROP VIEW IF EXISTS {raw_delete_import_view}")

        # 1) create raw_temp_table for n-n
        txt_raw_unnest_table = cls.txt_create_raw_import_view(
            schema_code, raw_import_table, raw_import_view, keys=[key], key_unnest=key
        )
        verbose and print(txt_raw_unnest_table)
        cls.c_sql_exec_txt(txt_raw_unnest_table)

        txt_process_table = cls.txt_create_processed_import_view(
            schema_code, raw_import_view, processed_import_view, keys=[key]
        )
        verbose and print(txt_process_table)
        cls.c_sql_exec_txt(txt_process_table)

        # 3) insert / update / delete ??

        # - delete : tout depuis raw_import_table
        # create_view for delete
        txt_raw_delete_table = cls.txt_create_raw_import_view(
            schema_code, raw_import_table, raw_delete_import_view, keys=[]
        )
        verbose and print(txt_raw_delete_table)
        cls.c_sql_exec_txt(txt_raw_delete_table)

        txt_processed_delete_table = cls.txt_create_processed_import_view(
            schema_code, raw_delete_import_view, processed_delete_import_view, keys=[]
        )
        verbose and print(txt_processed_delete_table)
        cls.c_sql_exec_txt(txt_processed_delete_table)

        txt_delete = f"""
DELETE FROM {cor_table} t
    USING {processed_delete_import_view} j
    WHERE t.{sm.pk_field_name()} = j.{sm.pk_field_name()}
    """
        cls.c_sql_exec_txt(txt_delete)

        # - insert
        txt_insert = cls.txt_import_view_to_insert(
            schema_code,
            processed_import_view,
            keys=[sm.pk_field_name(), rel.pk_field_name()],
            dest_table=cor_table,
        )
        verbose and print(txt_insert)
        cls.c_sql_exec_txt(txt_insert)

    @classmethod
    def bulk_import_process_csv(cls, schema_code, file_path, raw_import_table):
        """
        cree une vue a partir d'un fichier csv pour pouvoir traiter les données ensuite

        le fichier csv
            separateur : ';'
        créé
            - une table temporaire pour avoir les données du csv en varchar
            - une vue pour passer les champs en '' à NULL
        """

        with open(file_path, "r") as f:
            # on récupère la premiere ligne du csv pour avoir le nom des colonnes
            first_line = f.readline()

            # creation de la table temporaire
            txt_create_temporary_table_for_csv_import = (
                cls.txt_create_temporary_table_for_csv_import(raw_import_table, first_line)
            )
            cls.c_sql_exec_txt(txt_create_temporary_table_for_csv_import)

            # on copie les données dans la table temporaire
            txt_copy_from_csv = cls.txt_copy_from_csv(raw_import_table, first_line)
            db.session.connection().connection.cursor().copy_expert(txt_copy_from_csv, f)
            db.session.commit()

        return
