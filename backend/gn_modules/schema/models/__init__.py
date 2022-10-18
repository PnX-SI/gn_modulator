from .base import SchemaModelBase
from .column_properties import SchemaModelColumnProperties
from .existing import SchemaModelExisting


class SchemaModel(SchemaModelBase, SchemaModelColumnProperties, SchemaModelExisting):

    pass
