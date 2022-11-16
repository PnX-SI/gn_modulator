class DefinitionError(Exception):
    """
    Classe de base pour les erreurs de definitions
    """

    pass


class DefinitionNoDefsError(DefinitionError):
    """
    Quand un element de definition commençant par '_' n'est pas résolu (non trouvé dans les '_defs')
    """

    pass
