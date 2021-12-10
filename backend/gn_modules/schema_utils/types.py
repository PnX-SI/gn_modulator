cor_type = [
    {
        'definition': 'integer',
        'sql': 'INTEGER'
    },
    {
        'definition': 'boolean',
        'sql': 'BOOLEAN'
    },
        {
        'definition': 'number',
        'sql': 'FLOAT'
    },
    {
        'definition': 'string',
        'sql': 'VARCHAR'
    },
    {
        'definition': 'date',
        'sql': 'DATE'
    },
    {
        'definition': 'datetime',
        'sql': 'DATETIME'
    },
    {
        'definition': 'uuid',
        'sql': 'UUID'
    },
    {
        'definition': 'geometry',
        'sql': 'GEOMETRY'
    },
]


class SchemaTypes():
    '''
        types methods
    '''

    @classmethod
    def c_get_type(cls, type_in, field_name_in, field_name_out):
            return  next((item[field_name_out] for item in cor_type if item[field_name_in] == type_in), None)
