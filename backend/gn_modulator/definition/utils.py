import os
import json
import yaml
from pathlib import Path
from gn_modulator.utils.env import local_srid
from gn_modulator.utils.commons import replace_in_dict
from gn_modulator.utils.yaml import YmlLoader
from gn_modulator import MODULE_CODE


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
    def load_definition_from_file(cls, file_path):
        """
        Read json or yml file and return data
        """

        with open(file_path) as f:
            x = f.tell()
            if f.readline() == "#!nodef":
                return
            f.seek(x)
            data = yaml.load(f, YmlLoader) if file_path.suffix == ".yml" else json.load(f)

            # traitement du local_srid
            data = replace_in_dict(data, "__LOCAL_SRID__", local_srid())
            data = replace_in_dict(data, "__REF_MODULE_CODE__", MODULE_CODE)

            # on enleve aliases
            if isinstance(data, dict):
                data.pop("aliases", None)

            return data

    @classmethod
    def check_definition_element_in_list(cls, item, key_name, test_list, item_key=None):
        """
        on regarde
            si les élements d'un dictionnaire,
            ayant pour clé <key_name>
            ont des élément qui sont présent dans <test_list>

        par exemple
            - pour voir si les elements de clé 'schema_code'
              sont bien dans la liste des schema_code chargés dans le cache

        renvoie la liste des éléments manquants
        """

        missings = []

        # - dictionnaire
        if isinstance(item, dict):
            # patch pourris avec les data pour schema_code et commons.table_location
            if (
                key_name == "schema_code"
                and item.get("schema_code") == "commons.table_location"
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
