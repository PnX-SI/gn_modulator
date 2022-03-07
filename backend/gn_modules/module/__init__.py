from .base import ModuleBase
from .commands import ModuleCommands
from .migrations import ModuleMigration
class ModuleMethods(
    ModuleBase,
    ModuleCommands,
    ModuleMigration
):

    pass