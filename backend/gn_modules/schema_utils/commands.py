'''
    SchemaMethods : static methods for cmd
'''


class SchemaCommands:
    '''
        static methods for cmd
    '''

    @classmethod
    def c_get_sample(cls, schema_name, value, field_name=None):
        '''
            get one row from id
        '''

        sm = cls(schema_name)

        return sm.serialize(sm.get_row(value, field_name), fields=sm.columns().keys())
