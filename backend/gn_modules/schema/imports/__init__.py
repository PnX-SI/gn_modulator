from .base import SchemaBaseImports
from .bulk import SchemaBulkImports
from .utils import SchemaUtilsImports

class SchemaImports(
    SchemaBaseImports,
    SchemaBulkImports,
    SchemaUtilsImports
):
    '''
        methodes d'import de données
    '''
    pass