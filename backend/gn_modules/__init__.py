MODULE_CODE = "MODULES"
MODULE_PICTO = "fa-puzzle-piece"

from .definition import DefinitionMethods
from .schema import SchemaMethods
from .module import ModuleMethods
from gn_modules.utils.errors import get_errors
import time


def init_gn_modules():
    """
    Fonction d'initialisation de gn_module
    """

    # - definitions
    start_time = time.time()
    DefinitionMethods.init_definitions()
    print(f"definitions : {round((time.time() - start_time)*1e3)} ms")
    if get_errors():
        return

    # - schemas
    start_time = time.time()
    SchemaMethods.init_schemas()
    print(f"schemas     : {round((time.time() - start_time)*1e3)} ms")
    if get_errors():
        return

    # - modules
    start_time = time.time()
    ModuleMethods.init_modules()
    print(f"modules     : {round((time.time() - start_time)*1e3)} ms")
