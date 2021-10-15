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
from .schema_utils.commands import SchemaCommands

class SchemaMethods(
    SchemaApi,
    SchemaBase,
    SchemaCommands,
    SchemaConfig,
    SchemaFiles,
    SchemaModel,
    SchemaRepositories,
    SchemaSerializers,
    SchemaSql,
):

    _schema = {} # dict containing schema

    def __init__(self, group_name=None, object_name=None):
        if group_name and object_name:
            self.load(group_name, object_name)

    def __str__(self):
        return "< SchemaMethods : '{}'>".format(self.full_name())