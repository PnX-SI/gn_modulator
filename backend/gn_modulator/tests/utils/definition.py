"""
    fonctions pour les test sur les définitions
"""

from gn_modulator.utils.errors import get_errors, clear_errors, errors_txt
from gn_modulator.definition import DefinitionMethods
from gn_modulator.utils.cache import get_global_cache


def check_errors(definition=None, error_code=None, context=None):
    """
    si error_code is None
        - on verifie qu'il n'y pas d'erreur
    si error_code est définie
        - on vérifie qu'il n'y a qu'une seule erreur qui est bien de code == error_code
    """

    get_errors() and print(errors_txt())

    # si le code d'erreur n'est pas défini, on s'assure qu'il n'y a pas d'erreur
    if error_code is None:
        assert len(get_errors()) == 0, f"({context}) : il ne doit pas y avoir d'erreur à ce stade"

        definition
        assert definition is not None

        (
            definition_type,
            definition_code,
        ) = DefinitionMethods.get_definition_type_and_code(definition)

        assert definition_type is not None
        assert definition_code is not None

    else:
        assert (
            len(get_errors()) == 1
        ), f"({context}, {error_code}) : on s'attend à voir remonter seule erreur (et non {len(get_errors())})"

        # on teste si le code de l'erreur est celui attendu
        assert (
            get_errors()[0]["code"] == error_code
        ), f"({context}, {error_code}) : le code d'erreur attendu n' pas {get_errors()[0]['code']}"

        # on teste si la definition a bien été supprimé
        if (definition is not None) and (error_code not in ["ERR_LOAD_EXISTING"]):
            (
                definition_type,
                definition_code,
            ) = DefinitionMethods.get_definition_type_and_code(definition)
            assert (
                get_global_cache([definition_type, definition_code]) is None
            ), f"({context}, {error_code}) : la definition erronée aurait du être supprimée du cache"


def test_load_definition(file_path=None, error_code=None):
    """
    tests sur le chargement des fichiers yml
    et sur la remontée des erreurs
    lors de l'utilisation de la methode DefinitionMethods.load_definition_file
    """

    clear_errors()

    if file_path is None:
        return

    definition = DefinitionMethods.load_definition_file(file_path)

    check_errors(definition=definition, error_code=error_code, context="load_definition")

    return definition


def test_local_check_definition(file_path=None, error_code=None):
    """
    test sur l'utilisation et la remontée des erreurs
    de la méthode local_check_definition
    """

    clear_errors()

    if file_path is None:
        return

    # chargment de la definition (+ test que tout est ok)
    definition = test_load_definition(file_path)

    definition_type, definition_code = DefinitionMethods.get_definition_type_and_code(definition)

    DefinitionMethods.check_references()

    DefinitionMethods.local_check_definition(definition_type, definition_code)

    check_errors(definition=definition, error_code=error_code, context="local_check")

    return definition


def test_global_check_definition(file_path=None, error_code=None):
    """
    test sur l'utilisation et la remontée des erreurs
    de la méthode global_check_definition et associées
    TODO
    """

    clear_errors()

    if file_path is None:
        return

    definition = test_local_check_definition(file_path)

    definition_type, definition_code = DefinitionMethods.get_definition_type_and_code(definition)

    DefinitionMethods.global_check_definition(definition_type, definition_code)

    check_errors(definition=definition, error_code=error_code, context="global_check")

    return definition


def test_process_template(file_path=None, error_code=None):
    clear_errors()

    if file_path is None:
        return

    definition = test_load_definition(file_path)

    definition_type, definition_code = DefinitionMethods.get_definition_type_and_code(definition)

    DefinitionMethods.process_template(definition_type, definition_code)

    check_errors(definition=definition, error_code=error_code, context="process_template")
