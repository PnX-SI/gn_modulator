from .base import ModuleBase
from .commands import ModuleCommands
from .config import ModulesConfig
from .breadcrumbs import ModuleBreadCrumbs
from . import errors
from gn_modulator.utils.errors import add_error

from gn_modulator.utils.cache import get_global_cache, set_global_cache


class ModuleMethods(ModuleBase, ModuleBreadCrumbs, ModuleCommands, ModulesConfig):
    """
    Classe contenant les methodes de gestion des modules
    - config
    - initialisation
    - installation / mise à jour
    - suppression
    """

    errors = errors

    @classmethod
    def init_modules(cls):
        """
        Initialise la config des modules
        """

        for module_code in cls.module_codes():
            cls.init_module_config(module_code)

        for module_code in cls.module_codes():
            cls.process_fields(module_code)
