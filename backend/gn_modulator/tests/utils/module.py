from gn_modulator.definition import DefinitionMethods
from gn_modulator.module import ModuleMethods
from gn_modulator.utils.errors import get_errors


def load_module_from_file(file_path):
    """
    charge un module depuis un fichier
    """

    # ajout de la definition du module de test
    definition = DefinitionMethods.load_definition_file(file_path)

    if not definition:
        return

    module_code = definition.get("code")

    if not module_code:
        return

    DefinitionMethods.local_check_definition("module", module_code)
    print(get_errors())
    print(len(get_errors()))
    assert len(get_errors()) == 0

    DefinitionMethods.global_check_definition("module", module_code)
    assert len(get_errors()) == 0

    module_config = ModuleMethods.init_module_config(module_code)

    return module_config
