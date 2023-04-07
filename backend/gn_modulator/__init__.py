MODULE_CODE = "MODULATOR"
MODULE_PICTO = "fa-puzzle-piece"

from .definition import DefinitionMethods
from .schema import SchemaMethods
from .module import ModuleMethods
from gn_modulator.utils.errors import get_errors
from gn_modulator.utils.env import config_dir, config_modulator_dir
from gn_modulator.utils.files import symlink
import time


def init_gn_modulator():
    """
    Fonction d'initialisation de gn_module
    """

    if not (config_dir() / "modulator").is_dir():
        config_dir().mkdir(parents=True, exist_ok=True)
        symlink(config_modulator_dir, config_dir() / "modulator")

    verbose = False
    # - definitions
    start_time = time.time()
    DefinitionMethods.init_definitions()
    verbose and print(f"definitions : {round((time.time() - start_time)*1e3)} ms")
    if get_errors():
        return

    # - schemas
    start_time = time.time()
    SchemaMethods.init_schemas()
    verbose and print(f"schemas     : {round((time.time() - start_time)*1e3)} ms")
    if get_errors():
        return

    # - modules
    start_time = time.time()
    ModuleMethods.init_modules()
    verbose and print(f"modules     : {round((time.time() - start_time)*1e3)} ms")
