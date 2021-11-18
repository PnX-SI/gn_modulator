'''
    SchemaMethod : methods for schema processing

    class gathering methods from mixins
'''

from .schema_utils.api import SchemaApi
from .schema_utils.base import SchemaBase
from .schema_utils.commands import SchemaCommands
from .schema_utils.config.base import SchemaConfigBase
from .schema_utils.config.layout import SchemaConfigLayout
from .schema_utils.data import SchemaData
from .schema_utils.files import SchemaFiles
from .schema_utils.models import SchemaModel
from .schema_utils.process import SchemaProcess
from .schema_utils.repositories import SchemaRepositories
from .schema_utils.serializers import SchemaSerializers
from .schema_utils.sql import SchemaSql
from .schema_utils.validation import SchemaValidation

cache_schemas = {}


class SchemaMethods(
    SchemaApi,
    SchemaBase,
    SchemaCommands,
    SchemaConfigBase,
    SchemaConfigLayout,
    SchemaData,
    SchemaFiles,
    SchemaModel,
    SchemaProcess,
    SchemaRepositories,
    SchemaSerializers,
    SchemaSql,
    SchemaValidation
):

    _raw_schema = {}  # dict containing schema
    _processed_schema = {}  # dict containing schema
    _raw_schema = {}  # dict containing schema

    def __init__(self, schema_name=None):
        if schema_name:
            if schema_name in cache_schemas:
                return self.copy(cache_schemas[schema_name])
            self.load(schema_name)
            cache_schemas[schema_name] = self
            # self.MarshmallowSchema()


    def copy(self, sm):
        self._schema_name = sm._schema_name
        self._processed_schema = sm._processed_schema
        self._raw_schema = sm._raw_schema

    def __str__(self):
        return "< SchemaMethods : '{}'>".format(self.schema_name())
