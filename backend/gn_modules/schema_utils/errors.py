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

class SchemaProcessedPropertyError(Exception):
    '''
        Error when a property marked as processed has no processing instruction
    '''
    pass