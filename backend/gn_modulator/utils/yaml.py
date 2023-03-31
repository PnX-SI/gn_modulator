import yaml
import os
import json


class YmlLoader(yaml.CLoader):
    """
    pour ajouter des inclusion de fichier
    https://stackoverflow.com/questions/528281/how-can-i-include-a-yaml-file-inside-another
    """

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(YmlLoader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))

        with open(filename, "r") as f:
            if filename.endswith(".yml"):
                return yaml.load(f, YmlLoader)
            if filename.endswith(".json"):
                return json.loads(f)
            raise Exception(
                f"Wrong include {filename} in {self._root} (doest not end with .yml or .json)"
            )


YmlLoader.add_constructor("!include", YmlLoader.include)
