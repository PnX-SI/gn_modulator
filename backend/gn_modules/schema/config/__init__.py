from .base import SchemaConfigBase
from .filters import SchemaConfigFilters
from .grammar import SchemaConfigGrammar
from .layout import SchemaConfigLayout


class SchemaConfig(
    SchemaConfigBase, SchemaConfigFilters, SchemaConfigGrammar, SchemaConfigLayout
):
    """
    Classe qui englobe toutes les méthode pour la config
    """

    __abstract__ = True

    pass
