from .base import SchemaRepositoriesBase
from .cruved import SchemaRepositoriesCruved
from .filters import SchemaRepositoriesFilters
from .utils import SchemaRepositoriesUtil


class SchemaRepositories(
    SchemaRepositoriesBase,
    SchemaRepositoriesCruved,
    SchemaRepositoriesFilters,
    SchemaRepositoriesUtil,
):
    '''
        classe  qui regroupe les methode repositories
    '''

    __abstract__ = True
