from .base import SchemaSqlBase
from .constraint import SchemaSqlConstraint
from .index import SchemaSqlIndex
from .table import SchemaSqlTable
from .trigger import SchemaSqlTrigger


class SchemaSql(
    SchemaSqlBase,
    SchemaSqlConstraint,
    SchemaSqlIndex,
    SchemaSqlTable,
    SchemaSqlTrigger,
):
    '''
        Classe qui englobe toutes les méthode pour le sql
    '''

    __abstract__ = True

    pass
