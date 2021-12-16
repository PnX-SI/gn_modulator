from .base import SchemaSqlBase
from .constraint import SchemaSqlConstraint
from .table import SchemaSqlTable
from .trigger import SchemaSqlTrigger


class SchemaSql(
    SchemaSqlBase,
    SchemaSqlConstraint,
    SchemaSqlTable,
    SchemaSqlTrigger,
):
    '''
        Classe qui englobe toutes les méthode pour le sql
    '''

    __abstract__ = True

    pass
