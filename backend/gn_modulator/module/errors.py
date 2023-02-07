class ModuleDbError(Exception):
    pass


class ModuleConfigError(Exception):
    pass


class ModuleDefinitionFoundError(Exception):
    """
    Quand la definition d'un module n'est pas trouvée
    """

    pass


class ModuleNotFoundError(Exception):
    pass


class ModuleObjectNotFoundError(Exception):
    pass


class ModuleCodeRequiredError(Exception):
    pass


class ModuleDataNotInitialized(Exception):
    pass
