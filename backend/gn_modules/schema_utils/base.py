'''
    SchemaMethods : base methods for schemas

    - setters, getters
    - utils - schema parser
    - utils - file path 
    - load / save

'''
from jsonschema import validate

from .reference import schema_ref

processed_types = [
    'integer',
    'string'
]


class SchemaBase():

    # getters, setters

    def schema(self):
        '''
            getter
        '''
        return self._schema

    def set_schema(self, schema):
        '''
            setter
        '''
        self._schema = schema

    # utils - schema parser

    def module_code(self):
        '''
            returns module_code from self._schema['$meta']
        '''
        return self._schema['$meta']['module_code']

    def schema_name(self):
        '''
            returns schema_name from self._schema['$meta']
        '''
        return self._schema['$meta']['schema_name']

    def sql_schema_name(self):
        '''
            returns sql_schema_name from self._schema['$meta']
            can be 
              - defined in self._schema['$meta']['sql_schema_name'] 
              - or retrieved from module_code : 'm_{module_code}' 
        '''
        return self._schema['$meta'].get('sql_module_name', 'm_{}'.format(self.module_code()))

    def sql_table_name(self):
        '''
            !! can be confused with schema_name
            returns sql_table_name from self._schema['$meta']
            can be 
              - defined in self._schema['$meta']['sql_table_name'] 
              - or retrieved from module_code : 't_{schema_name}' 
        '''
        return self._schema['$meta'].get('sql_table_name', 't_{}'.format(self.schema_name()))
    
    def full_name(self, letter_case=None):
        '''
            return name
        '''
        if letter_case == 'pascal_case':
            return (
            self.full_name('snake_case')
            .replace('_', ' ')
            .title()
            .replace(' ', '')
        )
        if letter_case == 'snake_case':
            return '{}_{}'.format(self.module_code(), self.schema_name())
        else:
            return '{}.{}'.format(self.module_code(), self.schema_name())

    def pk_field_names(self):
        '''
            returns list of primary keys from self._schema['properties']
        '''

        pk_field_names = []
        for key, value in self.properties().items():
            if value.get('primary_key'):
                pk_field_names.append(key)
        return pk_field_names

    def pk_field_name(self):
        '''
            checks primary key uniqueness and returns it
        '''
        pk_field_names = self.pk_field_names()
        return (
            pk_field_names[0] if len(pk_field_names) == 1
            else None
        )

    def properties(self, processed_properties_only=False):
        '''
            returns a list of schema properties from self._schema['properties']

            TODO differentiate simple properties form relationships ??
        '''
        properties = self._schema['properties']

        if not processed_properties_only:
            return properties
        else:
            return {
                k: v
                for k,v in self.properties().items()
                if v['type'] in processed_types
            }

    def properties_array(self, processed_properties_only=False):
        '''
            return properties as array

            store properties key as 'name'
        '''

        properties_dict = self.properties(processed_properties_only=processed_properties_only)
        properties_array = []

        for k,v in properties_dict.items():
            v.update({'name': k})
            properties_array.append(v)

        return properties_array

    def processed_types(self):
        '''
            return processed_type (define on top of current file)
        '''
        return processed_types

    # validation

    def is_valid(self, schema):
        '''
            returns True if schema is valid according to schema_ref

            TODO
        '''
        return True # en attendant de travailler sur schema_ref
        try:
            validate(instance=schema, schema=schema_ref)
            return True
        except ValidationError as e :
            raise InvalidSchemaError('Invalid schema : {}'.format(e))
            return False

    def is_valid(self):
        '''
            returns True if self._schema is valid according to schema_ref
        '''
        return self.is_valid(self._schema)

    def validate_data(self, data):
        '''
            returns True if data is valid according to self._schema
        '''
        return validate(instance=data, schema=self._schema)


