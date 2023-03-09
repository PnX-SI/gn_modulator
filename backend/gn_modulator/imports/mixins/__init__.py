from pathlib import Path
from geonature.utils.env import db
from gn_modulator.definition import DefinitionMethods

from .check import ImportMixinCheck
from .data import ImportMixinData
from .insert import ImportMixinInsert
from .mapping import ImportMixinMapping
from .process import ImportMixinProcess
from .raw import ImportMixinRaw
from .relation import ImportMixinRelation
from .update import ImportMixinUpdate
from .utils import ImportMixinUtils


class ImportMixin(
    ImportMixinRelation,
    ImportMixinCheck,
    ImportMixinData,
    ImportMixinInsert,
    ImportMixinMapping,
    ImportMixinProcess,
    ImportMixinRaw,
    ImportMixinUpdate,
    ImportMixinUtils,
):
    def process_import_schema(self):

        self.init_import()
        if self.errors:
            return self
        db.session.flush()

        self.process_data_table()
        if self.errors:
            return self
        db.session.flush()

        self.process_mapping_view()
        if self.errors:
            return self
        db.session.flush()

        self.process_raw_view()
        if self.errors:
            return self
        db.session.flush()

        self.process_view()
        if self.errors:
            return self
        db.session.flush()

        self.process_check()
        if self.errors:
            return self
        db.session.flush()

        self.process_insert()
        if self.errors:
            return self
        db.session.flush()

        self.process_update()
        if self.errors:
            return self
        db.session.flush()

        self.process_relations()
        if self.errors:
            return self
        db.session.flush()

        self.res["nb_unchanged"] = (
            self.res["nb_process"] - self.res["nb_insert"] - self.res["nb_update"]
        )

        return self

    @classmethod
    def process_import_code(cls, import_code, data_dir_path):

        print(f"\nProcess scenaria d'import {import_code}")

        # get import definition
        import_definitions = DefinitionMethods.get_definition("import", import_code)
        import_definitions_file_path = DefinitionMethods.get_file_path("import", import_code)

        # for all definition items
        imports = []
        last_impt = None
        for import_definition in import_definitions["items"]:
            # récupération du fichier de données
            data_file_path = Path(data_dir_path) / import_definition["data"] if d.get("data") else Path(data_dir_path)

            # récupération du fichier pre-process, s'il est défini
            pre_process_file_path = (
                Path(import_definitions_file_path).parent / import_definition["pre_process"]
                if import_definition.get("pre_process")
                else None
            )

            impt = cls(schema_code=import_definition["schema_code"], data_dir_path=data_file_path, pre_process_file_path=pre_process_file_path)

            # pour éviter d'avoir à recharger
            if import_definition['keep_raw'] and last_impt:
                impt.tables['data'] = last_impt.tables['data']

            db.session.add(impt)
            # flush ??

            impt.process_import_schema()
            import_infos = impt.import_infos()
            if errors := import_infos["errors"]:
                print(f"Il y a des erreurs dans l'import {import_definition['schema_code']}")
                for error in errors:
                    print(f"- {error['code']} : {error['msg']}")
                return imports
            print(impt.pretty_infos())
            last_impt = impt

        print(f"\nImport {import_code} terminé\n")
        return imports
