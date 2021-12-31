'''
'''

from jsonschema import validate, RefResolver
from jsonschema.exceptions import ValidationError

# from .errors import SchemaValidationError


class SchemaValidation():
    '''
        Validation methods for schemas

        - validate_schema [classmethod]  validate schema
    '''

    # validation

    @classmethod
    def validate_schema(cls, schema_name, schema):
        '''
            returns True if schema is valid according to schema_ref
     TODO
        '''
        error = None
        reference_schema = cls.load_json_file_from_name('references.schema.schema')
        resolver = RefResolver(base_uri='file://{}/'.format(cls.config_directory()), referrer=reference_schema)
        validate(instance=schema, schema=reference_schema, resolver=resolver)

        try:

            validate(instance=schema, schema=reference_schema, resolver=resolver)

            # test id name
            if schema_name.replace('.', '/') != schema['$id']:
                error = (
                    'le champs $id={} ne correspond pas au nom du schema: {} (ref:{})'
                    .format(schema['$id'], schema_name, cls.reference_from_name(schema_name))
                )

        except ValidationError as e:
            error = e

        return error

    def validate_definition_schema(self):
        return self.cls().validate_schema(self.schema_name(), self.definition_schema())

    def validation_schema(self, schema):
        '''
            create validation schema from schema to accept None in case of
                number
                string

            exemple : 'number' => ['number', 'null']
        '''

        if type(schema) is list:
            return [self.validation_schema(elem) for elem in schema]

        if type(schema) is dict:

            if schema.get('type') in ['date', 'datetime', 'uuid']:
                schema['format'] = schema.get('type')
                schema['type'] = ['string', 'null']

            if schema.get('type') in ['number', 'string', 'integer', 'boolean', ]:
                schema['type'] = [schema['type'], 'null']

            else:
                return {key: self.validation_schema(elem) for key, elem in schema.items()}

        return schema

    def validate_data(self, data):
        '''
            returns True if data is valid according to self.schema(processed)
        '''

        error = None

        schema = self.schema('validation')

        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            error = e
        return error
