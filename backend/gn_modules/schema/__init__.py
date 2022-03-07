'''
    SchemaMethod : methods for schema processing

    class gathering methods from mixins
'''

from .api import SchemaApi
from .auto import SchemaAuto
from .base import SchemaBase
from .cache import SchemaCache
from .commands import SchemaCommands
from .config import SchemaConfig
from .doc import SchemaDoc
from .imports import SchemaImports
from .files import SchemaFiles
from .models import SchemaModel
from .process import SchemaProcess
from .repositories import SchemaRepositories
from .serializers import SchemaSerializers
from .sql import SchemaSql
from .types import SchemaTypes
from .validation import SchemaValidation
from . import errors

class SchemaMethods(
    SchemaApi,
    SchemaAuto,
    SchemaBase,
    SchemaCache,
    SchemaCommands,
    SchemaConfig,
    SchemaDoc,
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

    def __init__(self, schema_name):
        self._schema_name = schema_name
        if not self.get_schema_cache(schema_name, 'schema'):
            self.load()

    @property
    def cls(self):
        return self.__class__


    @property
    def definition(self):
        return self.cls.get_schema_cache(self.schema_name(), 'definition')

    @definition.setter
    def definition(self, value):
        self.cls.set_schema_cache(self.schema_name(), 'definition', value)

    @property
    def json_schema(self):
        return self.cls.get_schema_cache(self.schema_name(), 'json_schema')

    @json_schema.setter
    def json_schema(self, value):
        self.cls.set_schema_cache(self.schema_name(), 'json_schema', value)

    @property
    def validation_schema(self):
        return self.cls.get_schema_cache(self.schema_name(), 'validation_schema')

    @validation_schema.setter
    def validation_schema(self, value):
        self.cls.set_schema_cache(self.schema_name(), 'validation_schema', value)


    def __str__(self):
        return "< SchemaMethods : '{}'>".format(self.schema_name())
