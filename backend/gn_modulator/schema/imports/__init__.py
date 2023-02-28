from .base import SchemaBaseImports
from .bulk import SchemaBulkImports
from .data import SchemaDataImports
from .insert import SchemaInsertImports
from .update import SchemaUpdateImports
from .relation import SchemaRelationImports
from .preprocess import SchemaPreProcessImports
from .process import SchemaProcessImports
from .utils import SchemaUtilsImports


class SchemaImports(
    SchemaBaseImports,
    SchemaBulkImports,
    SchemaDataImports,
    SchemaInsertImports,
    SchemaUpdateImports,
    SchemaPreProcessImports,
    SchemaProcessImports,
    SchemaRelationImports,
    SchemaUtilsImports,
):
    """
    methodes d'import de données
    """

    pass
