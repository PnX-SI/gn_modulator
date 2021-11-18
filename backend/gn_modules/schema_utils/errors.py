'''
    Exceptions for schemas
'''


class SchemaLoadError(Exception):
    '''
        Error when loading a schema
    '''
    pass


class SchemaValidationError(Exception):
    '''
        Error when schema validation is wrong
    '''
    pass


class SchemaSqlError(Exception):
    '''
        Error in schema sql text processing
    '''
    pass


class SchemaUnautorizedSqlError(Exception):
    '''
        Error when we try to exec an sql code on an unautorized schema
    '''
    pass


class SchemaProcessedPropertyError(Exception):
    '''
        Error when a property marked as processed has no processing instruction
    '''
    pass


class SchemaRelationError(Exception):
    '''
        Error when a property marked as processed has no processing instruction
    '''
    pass


class SchemaRepositoryError(Exception):
    '''
        Error in a repositroy process
    '''
    pass


class SchemaRepositoryFilterError(Exception):
    '''
        Error when a filter is not correctly defined
    '''
    pass


class SchemaRepositoryFilterTypeError(Exception):
    '''
        Error when a filter is not correctly defined
    '''
    pass


class SchemaProcessConfigError(Exception):
    '''
        Error when a filter is not correctly defined
    '''
    pass


class SchemaDataTypeError(Exception):
    '''
        process_data : data_type is not valid
    '''
    pass


class SchemaDataPathError(Exception):
    '''
        process_data : data_path is not correct
    '''
    pass

class SchemaLayoutError(Exception):
    '''
        process_config layout
    '''
    pass
