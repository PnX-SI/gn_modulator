from .cache import get_global_cache, set_global_cache

"""
code erreurs
"""


def add_error(
    error_msg=None,
    error_code=None,
    definition_type=None,
    definition_code=None,
    file_path=None,
    template_file_path=None,
):
    if error_msg is None:
        raise Exception("error_msg is None")

    file_path = file_path or str(get_global_cache([definition_type, definition_code, "file_path"]))

    if definition_type and definition_code and (file_path is None):
        raise Exception(f"file path is None {definition_type}, {definition_code}")

    # if definition_type == "use_template":
    #     definition = get_global_cache([definition_type, definition_code, "definition"])
    #     template_code = definition["template_code"]
    #     template_file_path = get_global_cache(["template", template_code, "file_path"])
    #     if template_file_path is None:
    #         raise Exception(f"template file path is None {template_code}")

    error = {
        "error_msg": error_msg,
        "error_code": error_code,
        "file_path": str(file_path),
        "template_file_path": template_file_path,
        "definition_type": definition_type,
        "definition_code": definition_code,
    }

    get_errors().append(error)


def get_errors(definition_type=None, definition_code=None, error_code=None):
    errors = get_global_cache(["errors"])
    if errors is None:
        errors = []
        set_global_cache(["errors"], errors)

    if not ((definition_type or definition_code or error_code) and len(errors)):
        return errors

    filtered_errors = list(
        filter(
            lambda x: (definition_code is None or x.get("definition_code") == definition_code)
            and (definition_type is None or x.get("definition_type") == definition_type)
            and (error_code is None or error_code in x.get("error_code")),
            errors,
        )
    )

    return filtered_errors


def clear_errors():
    set_global_cache(["errors"], [])


def errors_txt():
    """
    Pour l'affichage de la liste des erreurs

    skip_no_error : ne renvoie rien s'il n'y a pas d'erreurs
    """

    errors = get_errors()

    txt_nb_errors = f"!!!! Il y a {len(errors)} erreurs dans les définitions. !!!!\n"

    txt_errors = txt_nb_errors

    if len(errors) == 0:
        return txt_errors

    # on liste les fichiers
    # afin de pouvoir les regrouper les erreurs par fichiers
    definition_error_file_paths = []
    template_file_paths = {}
    for definition_error in errors:
        if definition_error.get("template_file_path"):
            template_file_paths[definition_error.get("file_path")] = definition_error.get(
                "template_file_path"
            )

        if definition_error.get("file_path", "") not in definition_error_file_paths:
            definition_error_file_paths.append(str(definition_error.get("file_path", "")))

    # on trie les fichiers par ordre alphabetique
    # on affiche les erreurs par fichier pour simplifier la lecture
    for definition_error_file_path in sorted(definition_error_file_paths):
        txt_errors += f"\n- {definition_error_file_path}\n"
        if template_file_path := template_file_paths.get(definition_error_file_path):
            txt_errors += f"  {template_file_path}\n"

        txt_errors += "\n"

        for definition_error in filter(
            lambda x: x.get("file_path", "") == definition_error_file_path,
            errors,
        ):
            txt_errors += (
                f"  - {definition_error['error_code']} {definition_error['error_msg']}\n\n"
            )

    # Rappel du nombre d'erreur si élevé
    if len(errors) > 5:
        txt_errors += f"\n {txt_nb_errors}"

    return txt_errors
