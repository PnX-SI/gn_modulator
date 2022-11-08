class ModuleDbError(Exception):
    pass


class ModuleConfigError(Exception):
    pass


class ModuleNotFoundError(Exception):
    pass


class ModuleObjectNotFoundError(Exception):
    pass


class ModuleCodeRequiredError(Exception):
    pass


class ModuleDataNotInitialized(Exception):
    pass
