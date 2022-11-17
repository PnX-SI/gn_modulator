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
    errors = DefinitionMethods.init_definitions()
    print(f"definitions : {round((time.time() - start_time)*1e3)} ms")
    if errors:
        return errors

    # - schemas
    start_time = time.time()
    errors = SchemaMethods.init_schemas()
    print(f"schemas     : {round((time.time() - start_time)*1e3)} ms")
    if errors:
        return errors

    # - modules
    start_time = time.time()
    errors = ModuleMethods.init_modules()
    print(f"modules     : {round((time.time() - start_time)*1e3)} ms")
    if errors:
        return errors

    return errors
