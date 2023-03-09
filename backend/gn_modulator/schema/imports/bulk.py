from pathlib import Path

from geonature.utils.env import db

from gn_modulator.definition import DefinitionMethods
from gn_modulator.utils.env import schema_import
from gn_modulator.utils.cache import set_global_cache, get_global_cache


class SchemaBulkImports:
    @classmethod
    def process_import_code(
        cls, import_code, data_path, import_number=None, verbose=0, insert=False, commit=False
    ):
        """
        import_code est la référence du scenario d'import
        """

        if not import_number:
            import_number = cls.generate_import_number()

        print(f"\nProcess import {import_code} {import_code}")

        # get import definition
        import_definition = DefinitionMethods.get_definition("import", import_code)
        import_definition_file_path = DefinitionMethods.get_file_path("import", import_code)

        # for all definition items
        for d in import_definition["items"]:
            # récupération du fichier de données
            data_file_path = Path(data_path) / d["data"] if d.get("data") else Path(data_path)

            # récupération du fichier pre-process, s'il est défini
            pre_process_file_path = (
                Path(import_definition_file_path).parent / d["pre_process"]
                if d.get("pre_process")
                else None
            )

            # process import schema
            cls.process_import_schema(
                d["schema_code"],
                data_file_path,
                import_number=import_number,
                pre_process_file_path=pre_process_file_path,
                keep_raw=d.get("keep_raw"),
                verbose=verbose,
                insert=insert,
                commit=commit,
            )

            import_infos = cls.import_get_infos(import_number, d["schema_code"])

            if import_infos["errors"]:
                print(f"Il y a des erreurs dans l'import {d['schema_code']}")
                for error in errors:
                    print(f"- {error['code']} : {error['msg']}")
                return import_number

        print(f"\nImport {import_code} terminé\n")
        return import_number

    @classmethod
    def process_import_schema(
        cls,
        schema_code,
        data_file_path,
        import_number=None,
        pre_process_file_path=None,
        verbose=0,
        insert=False,
        keep_raw=False,
        commit=False,
    ):
        """
        import de données

        todo tout types de données
        """

        # 0) init
        #  suppression des table d'import précedentes ?
        # si keep_raw on garde la table qui contient les données csv

        if not import_number:
            import_number = cls.generate_import_number()

        cls.import_init(import_number, schema_code, data_file_path, pre_process_file_path)
        cls.import_clean_tables(import_number, schema_code, keep_raw)

        # 1) csv -> table temporaire
        #
        cls.import_process_data(
            import_number,
            schema_code,
            data_file_path,
            cls.import_get_infos(import_number, schema_code, "tables.import"),
            insert=insert,
            keep_raw=keep_raw,
        )
        if verbose and not keep_raw:
            print(f"\n-- import csv file {data_file_path.name}")
            print(f"   {cls.import_get_infos(import_number, schema_code, 'nb_data')} lignes")

        if cls.import_get_infos(import_number, schema_code, "errors"):
            return import_number
        # 2.1) pre-process
        #
        cls.import_preprocess(
            import_number,
            schema_code,
            cls.import_get_infos(import_number, schema_code, "tables.import"),
            cls.import_get_infos(import_number, schema_code, "tables.preprocess"),
            pre_process_file_path,
        )
        if cls.import_get_infos(import_number, schema_code, "errors"):
            return import_number

        # 2.2) table import (ou preprocess) -> vue brute
        cls.import_raw(
            import_number,
            schema_code,
            cls.import_get_infos(import_number, schema_code, "tables.preprocess"),
            cls.import_get_infos(import_number, schema_code, "tables.raw"),
        )
        if cls.import_get_infos(import_number, schema_code, "errors"):
            return import_number

        # 3) vue brute -> vue prête pour l'import avec les clés étrangéres et primaires résolues
        cls.import_process(
            import_number,
            schema_code,
            cls.import_get_infos(import_number, schema_code, "tables.raw"),
            cls.import_get_infos(import_number, schema_code, "tables.process"),
        )
        if cls.import_get_infos(import_number, schema_code, "errors"):
            return import_number

        # 4) INSERT / UPDATE
        # 4-1) INSERT
        cls.import_insert(
            import_number,
            schema_code,
            cls.import_get_infos(import_number, schema_code, "tables.process"),
        )
        if cls.import_get_infos(import_number, schema_code, "errors"):
            return import_number

        # 4-2) UPDATE
        cls.import_update(
            import_number,
            schema_code,
            cls.import_get_infos(import_number, schema_code, "tables.process"),
        )
        if cls.import_get_infos(import_number, schema_code, "errors"):
            return import_number
        ## HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # 4-2) UNCHANGED

        nb_unchanged = (
            cls.import_get_infos(import_number, schema_code, "nb_process")
            - cls.import_get_infos(import_number, schema_code, "nb_insert")
            - cls.import_get_infos(import_number, schema_code, "nb_update")
        )
        cls.import_set_infos(import_number, schema_code, "nb_unchanged", nb_unchanged)
        txt_pretty_info = cls.import_pretty_infos(import_number, schema_code)

        verbose and print(f"\n{txt_pretty_info}")

        # 5) process relations ???
        #  ?? au moins n-n
        cls.import_relations(
            import_number,
            schema_code,
            cls.import_get_infos(import_number, schema_code, "tables.preprocess", data_file_path),
            data_file_path,
            verbose,
        )

        if cls.import_get_infos(import_number, schema_code, "errors"):
            return import_number

        if commit:
            db.session.commit()

        return import_number
