from .cache import get_global_cache, set_global_cache

"""
code erreurs
"""


def add_error(msg=None, code=None, type=None, key=None, file_path=None):

    if msg is None:
        raise Exception("msg is NOne")

    if code is None:
        raise Exception("code is None")

    file_path = file_path or get_global_cache([type, key, "file_path"])

    if type and key and file_path is None:
        raise Exception(f"file path is None {type}, {key}")

    error = {"msg": msg, "code": code, "file_path": file_path}

    get_errors().append(error)


def get_errors():
    errors = get_global_cache(["errors"])
    if not isinstance(errors, list):
        errors = []
        set_global_cache(["errors"], errors)

    return errors


def clear_errors():
    set_global_cache(["errors"], [])


def errors_txt():
    """
    Pour l'affichage de la liste des erreurs
    """

    errors = get_errors()

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
            txt_errors += f"  - {definition_error['code']} {definition_error['msg']}\n"

    return txt_errors
