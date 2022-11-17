from .base import ModuleBase
from .commands import ModuleCommands
from .config import ModulesConfig
from .migrations import ModuleMigration
from .breadcrumbs import ModuleBreadCrumbs
from . import errors
from gn_modules.utils.cache import set_global_cache, get_global_cache


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

        init_modules_errors = []

        for module_code in cls.module_codes():
            try:
                init_modules_errors += cls.init_module_config(module_code)
                init_modules_errors += cls.process_module_assets(module_code)
            except Exception as e:
                if isinstance(e, errors.ModuleDefinitionFoundError):
                    init_modules_errors.append(
                        {
                            "type": "module",
                            "file_path": get_global_cache("module", module_code, "file_path"),
                            "msg": str(e),
                        }
                    )
                # TODO collecter les erreurs
                raise e

        return init_modules_errors
