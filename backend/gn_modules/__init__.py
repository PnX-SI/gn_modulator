MODULE_CODE = "MODULES"
MODULE_PICTO = "fa-puzzle-piece"

from .definition import DefinitionMethods
from .schema import SchemaMethods
from .module import ModuleMethods
import time


def init_gn_modules():
    """
    Fonction d'initialisation de gn_module
    """

    # - definitions

    start_time = time.time()
    init_gn_module_errors = DefinitionMethods.init_definitions()
    if init_gn_module_errors:
        return init_gn_module_errors
    print(f"definitions : {time.time() - start_time}")

    # - schemas
    start_time = time.time()
    init_gn_module_errors = SchemaMethods.init_schemas()
    if init_gn_module_errors:
        return init_gn_module_errors
    print(f"schemas     : {time.time() - start_time}")

    # - modules
    start_time = time.time()
    init_gn_module_errors = ModuleMethods.init_modules()
    if init_gn_module_errors:
        return init_gn_module_errors
    print(f"modules     : {time.time() - start_time}")

    return init_gn_module_errors
