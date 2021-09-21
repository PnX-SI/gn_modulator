'''
    SchemaMethod : methods for schema processing

    class gathering methods from mixins
'''

from .schema_utils.api import SchemaApi
from .schema_utils.base import SchemaBase
from .schema_utils.config import SchemaConfig
from .schema_utils.files import SchemaFiles
from .schema_utils.models import SchemaModel
from .schema_utils.repositories import SchemaRepositories
from .schema_utils.serializers import SchemaSerializers
from .schema_utils.sql import SchemaSql


class SchemaMethods(
    SchemaApi,
    SchemaBase,
    SchemaConfig,
    SchemaFiles, 
    SchemaModel,
    SchemaRepositories,
    SchemaSerializers,
    SchemaSql,
):

    _schema = {} # dict containing schema
    
    def __init__(self, module_code, schema_name):
        self.load(module_code, schema_name)
