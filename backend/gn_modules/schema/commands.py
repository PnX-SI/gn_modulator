"""
    SchemaMethods : static methods for cmd
"""


class SchemaCommands:
    """
    static methods for cmd
    """

    @classmethod
    def c_get_sample(cls, schema_code, value, field_name=None):
        """
        get one row from id
        """

        sm = cls(schema_code)

        return sm.serialize(sm.get_row(value, field_name), fields=sm.columns().keys())
