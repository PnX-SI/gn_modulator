from pathlib import Path
from geonature.utils.env import db
from gn_modulator.definition import DefinitionMethods

from .check import ImportMixinCheck
from .count import ImportMixinCount
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
    ImportMixinCount,
    ImportMixinData,
    ImportMixinInsert,
    ImportMixinMapping,
    ImportMixinProcess,
    ImportMixinRaw,
    ImportMixinUpdate,
    ImportMixinUtils,
):
    def process_import_schema(self):
        if self.status in ["DONE", "PROCESSING"]:
            return

        if self.status is None:
            self.process_load_data_and_check()

        if self.status == "ERROR":
            return

        if self.options.get("check_only") and not self.status == "READY":
            self.status = "READY"
            return self

        self.process_insert_and_update()

    def process_load_data_and_check(self):
        for action in [
            "init_import",
            "process_data_table",
            "process_mapping_view",
            "process_pre_check",
            "process_raw_view",
            "process_view",
            "process_post_check",
            "process_count",
        ]:
            getattr(self, action)()
            if self.status == "ERROR":
                return self
            db.session.flush()

    def process_insert_and_update(self):
        self.status = "PROCESSING"

        for action in [
            "process_insert",
            "process_update",
            "process_relations",
        ]:
            getattr(self, action)()
            if self.status == "ERROR":
                return self
            db.session.flush()

        self.status = "DONE"

    @classmethod
    def process_import_code(cls, import_code, data_dir_path, insert_data=True, commit=True):
        # get import definition
        import_definitions = DefinitionMethods.get_definition("import", import_code)

        if not import_definitions:
            return None

        print(f"\nProcess scenario d'import {import_code}")

        import_definitions_file_path = DefinitionMethods.get_file_path("import", import_code)

        # for all definition items
        imports = []
        for import_definition in import_definitions["items"]:
            # récupération du fichier de données
            data_file_path = (
                Path(data_dir_path) / import_definition["data"]
                if import_definition.get("data")
                else Path(data_dir_path)
            )

            # récupération du fichier pre-process, s'il est défini
            mapping_file_path = (
                Path(import_definitions_file_path).parent / import_definition["mapping"]
                if import_definition.get("mapping")
                else None
            )

            impt = cls(
                module_code=import_definition["module_code"],
                object_code=import_definition["object_code"],
                data_file_path=data_file_path,
                mapping_file_path=mapping_file_path,
                options={"insert_data": False},
            )

            # pour éviter d'avoir à recharger les données
            if import_definition.get("keep_raw") and len(imports):
                impt.tables["data"] = imports[-1].tables["data"]

            db.session.add(impt)
            # flush ??

            impt.process_import_schema()
            imports.append(impt)

            if commit:
                db.session.commit()

            if impt.errors:
                print(f"Il y a des erreurs dans l'import {import_definition['object_code']}")
                for error in impt.errors:
                    print(f"- {error['code']} : {error['msg']}")
                return imports
            print(impt.pretty_infos())

        print(f"Import {import_code} terminé")
        return imports
