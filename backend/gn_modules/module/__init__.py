from .base import ModuleBase
from .commands import ModuleCommands
from .config import ModulesConfig
from .migrations import ModuleMigration
from .breadcrumbs import ModulesBreadCrumbs


class ModuleMethods(
    ModuleBase, ModulesBreadCrumbs, ModuleCommands, ModulesConfig, ModuleMigration
):

    pass
