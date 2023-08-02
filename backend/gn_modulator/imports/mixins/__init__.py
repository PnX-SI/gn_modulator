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
        """
        fonction du processus d'import
        """

        # si le process est terminé ou en cours
        if self.status in ["DONE", "PROCESSING"]:
            return self

        # étape de chargement et de vérification
        if self.status is None:
            self.process_load_data_and_check()

        # process en erreur
        if self.status == "ERROR":
            return self

        # si le processus est en deux étapes
        # on sort après la phase de vérification
        if self.options.get("check_only") and self.status != "READY":
            self.status = "READY"
            return self

        # phase d'insertion et de modification des données
        self.process_insert_and_update()

    def process_load_data_and_check(self):
        """
        fonction pour le chargement et la vérification des données
        """

        for action in [
            "init_import",
            "process_data_table",
            "process_mapping_view",
            "process_pre_check",
            "process_raw_view",
            "process_view",
            "process_relations_view",
            "process_post_check",
            "process_count",
        ]:
            getattr(self, action)()

            # en cas d'erreur on arrête le processus
            if self.status == "ERROR":
                return self

            db.session.flush()

    def process_insert_and_update(self):
        """
        fonction pour l'insertion (et la mise à jour) des données
        """
        self.status = "PROCESSING"

        for action in [
            "process_insert",
            "process_update",
            "process_relations_data",
        ]:
            getattr(self, action)()

            # en cas d'erreur on arrête le processus
            if self.status == "ERROR":
                return self

            db.session.flush()

        # import effectué
        self.status = "DONE"

    @classmethod
    def process_import_code(cls, import_code, data_dir_path=None, insert_data=False, commit=True):
        """
        fonction pour réaliser un scénario d'import

        import_code: code du scénario d'import
        data_dir_path: chemin du répertoire contenant les données
        insert_data: si l'on choisit de mettre les données en base
          - on avec 'INSERT' (pour les tests)
          - avec 'COPY'
        commit: si l'on choisit de commiter les transactions
           - on ne le fait pas pour les tests
        """

        # Récupération du scénario d'import
        import_definitions = DefinitionMethods.get_definition("import", import_code)

        if not import_definitions:
            return None

        print(f"\nProcess scenario d'import {import_code}")

        # Récupération du chemin du fichier
        #  - pour avoir accès aux éventuels fichiers de mapping
        import_definitions_file_path = DefinitionMethods.get_file_path("import", import_code)

        # tableau pour stocker les instances d'import
        # - pour du log ou du debug
        imports = []

        data_dir_path = data_dir_path or import_definitions_file_path.parent / "data"

        # Pour tous les imports du scénario
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

            # creation de l'instance d'import
            impt = cls(
                module_code=import_definition["module_code"],
                object_code=import_definition["object_code"],
                data_file_path=data_file_path,
                mapping_file_path=mapping_file_path,
                options={"insert_data": insert_data},  # ici insert data permet de choi
            )

            # pour éviter d'avoir à recharger les données
            if import_definition.get("keep_raw") and len(imports):
                impt.tables["data"] = imports[-1].tables["data"]

            # ajout d'un nouvelles instance d'import en base
            db.session.add(impt)

            # process d'import
            impt.process_import_schema()

            # ajout à la liste d'import
            imports.append(impt)

            # commit des transactions
            if commit:
                db.session.commit()

            # En cas d'erreur on sort
            if impt.errors:
                print(f"Il y a des erreurs dans l'import {import_definition['object_code']}")
                for error in impt.errors:
                    print(f"- {error['error_code']} : {error['error_msg']}")
                return imports

            # affichage des résultats
            print(impt.pretty_infos())

        print(f"Import {import_code} terminé")
        return imports
