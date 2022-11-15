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
        return {
            key: replace_in_dict(val, value_test, value) for key, val in data.items()
        }

    if isinstance(data, list):
        return [replace_in_dict(item, value_test, value) for item in data]

    if isinstance(data, str):
        if data == value_test:
            return value
        if value_test in data:
            return data.replace(value_test, str(value))

    return data


def errors_txt(errors):
    """
    Pour l'affichage de la liste des erreurs
    """

    txt_errors = f"Il y a {len(errors)} erreurs dans les définitions.\n"

    if len(errors) == 0:
        return txt_errors

    # on liste les fichiers pour pouvoir les regrouper ensuite
    definition_error_file_paths = []
    for definition_error in errors:
        if definition_error["file_path"] not in definition_error_file_paths:
            definition_error_file_paths.append(definition_error["file_path"])

    # on trie les fichiers par ordre alphabetique
    # on affiche les erreurs par fichier pour simplifier la lecture
    for definition_error_file_path in sorted(definition_error_file_paths):
        txt_errors += f"\n- {definition_error_file_path}\n"

        for definition_error in filter(
            lambda x: x["file_path"] == definition_error_file_path,
            errors,
        ):
            txt_errors += f"  - {definition_error['msg']}\n"
            # txt_errors += f"    {definition_error['msg']}\n"

    return txt_errors
