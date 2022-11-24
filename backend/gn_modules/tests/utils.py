from gn_modules.definition import DefinitionMethods
from gn_modules.module import ModuleMethods


def load_module_from_file(file_path):
    """
    charge un module depuis un fichier
    """

    # ajout de la definition du module de test
    definition = DefinitionMethods.load_definition_file(file_path)

    if not definition:
        return

    module_code = definition.get("module_code")

    if not module_code:
        return

    DefinitionMethods.local_check_definition("module", module_code)

    DefinitionMethods.global_check_definition("module", module_code)

    module_config = ModuleMethods.init_module_config(module_code)

    return module_config
