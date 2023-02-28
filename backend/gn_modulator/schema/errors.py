"""
    Exceptions for schemas
"""


class SchemaError(Exception):
    pass


class SchemaNameError(SchemaError):
    """
    schema not found
    """

    pass


class SchemaNotFoundError(SchemaError):
    """
    Error when loading a schema
        schema file not found
    """

    pass


class SchemaValidationError(SchemaError):
    """
    Error when schema validation is wrong
    """

    pass


class SchemaSqlError(SchemaError):
    """
    Error in schema sql text processing
    """

    pass


class SchemaUnautorizedSqlError(SchemaSqlError):
    """
    Error when we try to exec an sql code on an unautorized schema
    """

    pass


class SchemaProcessedPropertyError(SchemaError):
    """
    Error when a property marked as processed has no processing instruction
    """

    pass


class SchemaSerializerModelIsNoneError(SchemaError):
    """
    Error when a relation None during marshmallow serializer/deserializer creation
    """

    pass


class SchemaImportError(SchemaError):
    pass


class SchemaImportPKError(SchemaImportError):
    """
    Error when a property marked as processed has no processing instruction
    """

    pass


class SchemaImportRequiredInfoNotFoundError(SchemaImportError):
    pass


class SchemaRelationError(SchemaError):
    """
    Error when a property marked as processed has no processing instruction
    """

    pass


class SchemaRepositoryError(SchemaError):
    """
    Error in a repositroy process
    """

    pass


class SchemaRepositoryFilterError(SchemaRepositoryError):
    """
    Error when a filter is not correctly defined
    """

    pass


class SchemaRepositoryFilterTypeError(SchemaRepositoryError):
    """
    Error when a filter is not correctly defined
    """

    pass


class SchemaProcessConfigError(SchemaError):
    """
    Error when a filter is not correctly defined
    """

    pass


class objectDataTypeError(SchemaError):
    """
    process_data : data_type is not valid
    """

    pass


class objectDataPathError(SchemaError):
    """
    process_data : data_path is not correct
    """

    pass


class SchemaLayoutError(SchemaError):
    """
    process_config layout
    """

    pass


class SchemaAutoError(SchemaError):
    """
    Schema Auto Generation Error
    """

    pass


class SchemaUnsufficientCruvedRigth(SchemaError):
    """
    When cruved is not enougth
    """

    pass


class SchemaModelColumnPropertyError(SchemaError):
    pass


class SchemaGrammarTypeError(SchemaError):
    pass
