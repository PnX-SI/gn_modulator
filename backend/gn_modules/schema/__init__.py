"""
    SchemaMethod : methods for schema processing

    class gathering methods from mixins
"""

from .api import SchemaApi
from .auto import SchemaAuto
from .base import SchemaBase
from .commands import SchemaCommands
from .config import SchemaConfig
from .doc import SchemaDoc
from .export import SchemaExport
from .imports import SchemaImports
from .models import SchemaModel
from .repositories import SchemaRepositories
from .serializers import SchemaSerializers
from .sql import SchemaSql
from .types import SchemaTypes
from .validation import SchemaValidation
from . import errors
from gn_modules.utils.cache import get_global_cache, set_global_cache


class SchemaMethods(
    SchemaApi,
    SchemaAuto,
    SchemaBase,
    SchemaCommands,
    SchemaConfig,
    SchemaDoc,
    SchemaExport,
    SchemaImports,
    SchemaModel,
    SchemaRepositories,
    SchemaSerializers,
    SchemaSql,
    SchemaTypes,
    SchemaValidation,
):

    errors = errors

    def __init__(self, schema_code):
        self._schema_code = schema_code
        if not get_global_cache(["schema", schema_code, "schema"]):
            self.init()

    @property
    def cls(self):
        return self.__class__

    @property
    def definition(self):
        return get_global_cache(["schema", self.schema_code(), "definition"])

    @definition.setter
    def definition(self, value):
        set_global_cache(["schema", self.schema_code(), "definition"], value)

    @property
    def json_schema(self):
        return get_global_cache(["schema", self.schema_code(), "json_schema"])

    @json_schema.setter
    def json_schema(self, value):
        set_global_cache(["schema", self.schema_code(), "json_schema"], value)

    def __str__(self):
        return self.schema_code()

    def init(self):
        """
        Initialise le schema et le place dans le cache
        """

        definition = self.definition
        schema_code = definition["code"]

        if not definition:
            raise errors.SchemaLoadError(
                "pas de definition pour le schema: {}".format(schema_code)
            )

        set_global_cache(["schema", schema_code, "schema"], self)

        self.definition = definition

        if self.autoschema():
            self.definition = self.get_autoschema()

        self.process_backrefs()

        self.json_schema = self.get_json_schema()

        return self

    @classmethod
    def init_schemas(cls):
        """
        Initialise l'ensemble des schémas
        """
        # init class
        for schema_codes in cls.schema_codes():
            SchemaMethods(schema_codes)

        # init Model
        for schema_codes in cls.schema_codes():
            SchemaMethods(schema_codes).Model()
        for schema_codes in cls.schema_codes():
            SchemaMethods(schema_codes).MarshmallowSchema()
