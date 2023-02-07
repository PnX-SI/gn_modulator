from .base import ModuleBase
from .commands import ModuleCommands
from .config import ModulesConfig
from .migrations import ModuleMigration
from .breadcrumbs import ModuleBreadCrumbs
from . import errors
from gn_modulator.utils.errors import add_error


class ModuleMethods(ModuleBase, ModuleBreadCrumbs, ModuleCommands, ModulesConfig, ModuleMigration):
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
            cls.process_module_assets(module_code)
