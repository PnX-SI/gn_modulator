'''
    SchemaMethod : methods for schema processing

    class gathering methods from mixins
'''

from .schema_utils.api import SchemaApi
from .schema_utils.auto import SchemaAuto
from .schema_utils.base import SchemaBase
from .schema_utils.commands import SchemaCommands
from .schema_utils.config import SchemaConfig
from .schema_utils.imports import SchemaImports
from .schema_utils.files import SchemaFiles
from .schema_utils.models import SchemaModel
from .schema_utils.process import SchemaProcess
from .schema_utils.repositories import SchemaRepositories
from .schema_utils.serializers import SchemaSerializers
from .schema_utils.sql import SchemaSql
from .schema_utils.types import SchemaTypes
from .schema_utils.validation import SchemaValidation


cache_schemas = {}


class SchemaMethods(
    SchemaApi,
    SchemaAuto,
    SchemaBase,
    SchemaCommands,
    SchemaConfig,
    SchemaImports,
    SchemaFiles,
    SchemaModel,
    SchemaProcess,
    SchemaRepositories,
    SchemaSerializers,
    SchemaSql,
    SchemaTypes,
    SchemaValidation
):

    _schemas = {}

    def __init__(self, schema_name=None):
        if schema_name:
            if schema_name in cache_schemas:
                return self.copy(cache_schemas[schema_name])
            self.load(schema_name)
            cache_schemas[schema_name] = self

    def copy(self, sm):
        self._schema_name = sm._schema_name
        self._schemas = sm._schemas

    def __str__(self):
        return "< SchemaMethods : '{}'>".format(self.schema_name())
