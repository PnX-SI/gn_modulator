import copy
import os
import json
import yaml
from pathlib import Path
from gn_modules.utils.env import local_srid


class DefinitionUtils:
    """
    methodes pour
    - lire les json et yaml
    """

    @classmethod
    def get_key_file_paths(cls, file_path):
        key_file_paths = {}
        file_name = file_path.stem
        for root, dirs, files in os.walk(file_path.parent):
            for file in filter(
                lambda f: (
                    f.suffix == ".yml"
                    and f.stem.startswith(file_name)
                    and len(f.stem.split("-")) == 2
                ),
                map(lambda f: Path(f), files),
            ):
                key = file.stem.split("-")[1]
                key_file_paths[key] = Path(root) / file

            # on ne fait pas les sous répertoires
            break

        return key_file_paths

    @classmethod
    def load_definition_from_file(cls, file_path, load_keys=False):
        """
        Read json or yml file and return data

        TODO process error
        """
        if load_keys:
            data = cls.load_definition_from_file(file_path)
            # get all files

            for key, key_file_path in cls.get_key_file_paths(file_path).items():
                data[key] = cls.load_definition_from_file(key_file_path)

            return data

        with open(file_path) as f:
            data_txt = f.read()
            # traitement du local_srid
            data_txt = data_txt.replace("__LOCAL_SRID__", str(local_srid()))
            data = (
                yaml.load(data_txt, yaml.CLoader)
                if file_path.suffix == ".yml"
                else json.loads(data_txt)
            )
            return data

    @classmethod
    def check_definition_element_in_list(cls, item, key_name, test_list, item_key=None):
        """
        on regarde
            si les élements d'un dictionnaire,
            ayant pour clé <key_name>
            ont des élément qui sont présent dans <test_list>

        par exemple
            - pour voir si les elements de clé 'schema_name'
              sont bien dans la liste des schema_name chargés dans le cache

        renvoie la liste des éléments manquants
        """

        missings = []

        # - dictionnaire
        if isinstance(item, dict):

            # patch pourris avec les data pour schema_name et commons.table_location
            if (
                key_name == "schema_name"
                and item.get("schema_name") == "commons.table_location"
                and item.get("items")
            ):
                return []

            for item_key, item_value in item.items():
                missings += cls.check_definition_element_in_list(
                    item_value, key_name, test_list, item_key
                )
            return missings

        # - liste
        if isinstance(item, list):
            for item_value in item:
                missings += cls.check_definition_element_in_list(item_value, key_name, test_list)

        # - element
        if item_key == key_name and isinstance(item, str):
            if item not in test_list:
                missings = [item]

        return missings

    @classmethod
    def errors_txt(cls, errors):
        """
        Pour l'affichage de la liste des erreurs
        """

        txt_errors = f"!!!! Il y a {len(errors)} erreurs dans les définitions. !!!!\n"

        if len(errors) == 0:
            return txt_errors

        # on liste les fichiers
        # afin de pouvoir les regrouper les erreurs par fichiers
        definition_error_file_paths = []
        for definition_error in errors:
            if definition_error.get("file_path", "") not in definition_error_file_paths:
                definition_error_file_paths.append(definition_error.get("file_path", ""))

        # on trie les fichiers par ordre alphabetique
        # on affiche les erreurs par fichier pour simplifier la lecture
        for definition_error_file_path in sorted(definition_error_file_paths):
            txt_errors += f"\n- {definition_error_file_path}\n\n"

            for definition_error in filter(
                lambda x: x.get("file_path", "") == definition_error_file_path,
                errors,
            ):
                txt_errors += f"  - {definition_error['msg']}\n"

        return txt_errors
