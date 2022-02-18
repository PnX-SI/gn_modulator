'''
'''

from pathlib import Path
from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError
from jsonschema import Draft7Validator
# from .errors import SchemaValidationError


class SchemaValidation():
    '''
        Validation methods for schemas

        - validate_schema [classmethod]  validate schema
    '''

    # validation


    @classmethod
    def check_reference(cls, schema):
        '''
            returns True if schema is valid according to schema_ref
     TODO
        '''

        Draft7Validator.check_schema(schema)

    @classmethod
    def check_definition(cls, definition):
        '''
            returns True if schema is valid according to schema_ref
     TODO
        '''

        autoschema = definition.get('meta', {}).get('autoschema')

        definition_reference = (
            cls.get_global_cache('reference','definition_auto') if autoschema
            else cls.get_global_cache('reference','definition')
        )
        resolver = RefResolver(base_uri='file://{}/'.format(cls.config_directory()), referrer=definition_reference)
        validate(instance=definition, schema=definition_reference, resolver=resolver)


    @classmethod
    def validate_schema(cls, schema, reference_name=None):
        '''
            returns True if schema is valid according to schema_ref
     TODO
        '''
        error = None
        reference_schema = cls.get_global_cache('reference',reference_name)

        if reference_schema:
            validate(instance=schema, schema=reference_schema)
        else:
            validators.check_schema(schema)

        return True

    def validate_definition_schema(self):
        return self.cls.validate_schema(self.schema_name(), self.definition_schema())


    def validate_data(self, data):
        '''
        '''

        validate(instance=data, schema=self.validation_schema)
