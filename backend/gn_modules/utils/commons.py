"""
    utils, patch, etc...
"""


import unicodedata


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
