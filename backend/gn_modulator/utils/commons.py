"""
    utils, patch, etc...
"""


import unicodedata
import sys
from importlib import import_module


def unaccent(input_str):
    """
    remove accent
    https://stackoverflow.com/a/517974
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def replace_in_dict(data, value_test, value):
    """
     replace dans un dictionnaire
     par ex:
         value_test = ':id_module'
         value = 17
    ':id_module' -> 17
    'le modude d'id = :id_module' -> 'le modude d'id = 17'
    """

    # # test avec json
    # value_ = (
    #     json.dumps(value)
    #     if isinstance(value, dict) or isinstance(value, list)
    #     else "true"
    #     if value is True
    #     else "false"
    #     if value is False
    #     else "null"
    #     if value is None
    #     else str(value)
    #     if isinstance(value, int) or isinstance(value, float)
    #     else value
    # )
    # return json.loads(json.dumps(data).replace(value_test, value_))

    if isinstance(data, dict):
        return {key: replace_in_dict(val, value_test, value) for key, val in data.items()}

    if isinstance(data, list):
        return [replace_in_dict(item, value_test, value) for item in data]

    if isinstance(data, str):
        if data == value_test:
            return value
        if value_test in data:
            return data.replace(value_test, str(value))

    return data


def get_class_from_path(path):
    class_module_name, class_object_name = path.rsplit(".", 1)
    class_module = import_module(class_module_name)
    return getattr(class_module, class_object_name)


def getAttr(obj, path, index=0):
    """
    pour récupérer des valeurs dans un dict avec des clé en key1.key2 (récursif)
    """
    if obj is None:
        return obj

    if isinstance(path, str):
        return getAttr(obj, path.split("."), index)

    if isinstance(path, list):
        if index > len(path) - 1:
            return obj
        path_cur = path[index]
        cur = obj[path_cur]
        return getAttr(cur, path, index + 1)


def test_is_app_running():
    """
    On teste sys.argv pour éviter de charger les définitions
        si on est dans le cadre d'une commande
    On initialise dans le cadre d'une application lancée avec
        - gunicorn
        - celery
        - pytest
        - flask run
        - geonature run
    """

    return any(sys.argv[0].endswith(x) for x in ["gunicorn", "celery", "pytest"]) or (
        len(sys.argv) >= 2 and sys.argv[1] == "run"
    )
