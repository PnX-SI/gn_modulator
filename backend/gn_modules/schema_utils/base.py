'''
    SchemaMethods : base methods for schemas

    - setters, getters
    - utils - schema parser
    - utils - file path 
    - load / save

'''
import gc

from jsonschema import validate, RefResolver

from .reference import schema_ref

processed_types = [
    'integer',
    'number',
    'text',
    'geom',
    'date',
    'uuid'
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

    def id(self):
        return self._schema['$id']

    def group_name(self):
        '''
            returns group_name from self._schema['$meta']
        '''
        return self._schema['$meta']['group_name']

    def object_name(self):
        '''
            returns object_name from self._schema['$meta']
        '''
        return self._schema['$meta']['object_name']

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
        if letter_case in ['snake_case', '_']:
            return '{}_{}'.format(self.group_name(), self.object_name())
        if letter_case == '/':
            return '{}/{}'.format(self.group_name(), self.object_name())
        else:
            return '{}.{}'.format(self.group_name(), self.object_name())



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

    def code_field_name(self):
        return self._schema['$meta'].get('code_field_name', '{}_code'.format(self.object_name()))

    def name_field_name(self):
        return self._schema['$meta'].get('name_field_name', '{}_name'.format(self.object_name()))


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
                if v.get('type') in processed_types
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

    def get_property(self, key):
        '''
        '''
        return self._schema['properties'][key]

    def get_relation(self, key):
        '''
        '''
        relation_reference =  self._schema['properties'][key]['$ref']
        return self.__class__().load_from_reference(relation_reference)


    def relationships(self):
        '''
            return dict of relationship (from _schema['$meta']['properties'])
        '''
        return {
            k: v
            for k,v in self.properties().items()
            if v.get('type') == 'object'
        }



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
        resolver = RefResolver('file://%s/' % self.schemas_dir(), None)

        return validate(instance=data, schema=self._schema, resolver=resolver)

    def get_class_from_cache(self, name, Base):
        '''
            return class from ''cache''

            for Models, MarshMallowSchemas, etc...
        '''
        all_refs = gc.get_referrers(Base)
        results = []
        for obj in all_refs:
            if (isinstance(obj, tuple)) and obj[0].__name__ ==  name:
                return obj[0]
        return None