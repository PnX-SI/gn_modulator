'''
    SchemaMethods : base methods for schemas

    - setters, getters
    - utils - schema parser

'''

import copy
import json
import re

from geonature.utils.config import config
from sqlalchemy.util.langhelpers import portable_instancemethod

from .errors import SchemaProcessConfigError, SchemaRelationError

column_types = [
    'integer',
    'number',
    'string',
    'geometry',
    'date',
    'date_time',
    'boolean',
    'uuid'
]


class SchemaBase():
    '''
        - cls           : self.__class__
        - log           : log message
        - pprint        : pretty print for dict
        - schema
        - set_schema
    '''

    # getters, setters

    @classmethod
    def log(cls, msg):
        '''
            Pour les log, print pour l'instant
            TODO
        '''
        print('{}'.format(msg))

    @classmethod
    def pprint(cls, d, indent=2):
        print(json.dumps(d, indent=indent, sort_keys=True, ensure_ascii=False))

    def get_schema(self, columns_only=False):

        # import pdb; pdb.set_trace()
        schema = self.json_schema

        if columns_only:
            schema = copy.deepcopy(schema)
            schema['properties'] = {
                key: column_def
                for key, column_def in schema['properties'].items()
                if key in self.column_keys()
            }

        return schema

    # utils - schema parser

    def required(self):
        return self.definition.get('required', [])

    def is_required(self, key):

        return (
            self.properties()[key].get('required') or key in self.required() if key in self.properties()
            else False
        )

    def attr(self, prop=None, default=None):
        '''
            renvoie
            - $meta si prop est null
            - $meta['prop1']['prop2']['prop3'] si prop = 'prop1.prop2.prop3'

            ou $meta.prop
        '''

        elem = self.definition

        if not prop:
            return elem

        for prop_path in prop.split('.'):
            if not isinstance(elem, dict):
                return default
            elem = elem.get(prop_path, None)
            if elem is None:
                return default

        return elem or default


    def schema_name(self, letter_case=None):
        '''
            return name
        '''

        schema_name = self._schema_name

        if letter_case == 'pascal_case':
            return (
                schema_name
                    .replace('.', ' ')
                    .title()
                    .replace(' ', '')
            )
        if letter_case in ['snake_case', '_']:
            return schema_name.replace('.', '_')
        if letter_case == '/':
            return schema_name.replace('.', '/')
        else:
            return schema_name

    def pk_field_names(self):
        '''
            returns list of primary keys from self.definition_schema['properties']
        '''

        pk_field_names = []
        for key, column_def in self.columns().items():
            if column_def.get('primary_key'):
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

    def object_name(self):
        return self.schema_name().split('.')[-1]

    def group_name(self):
        return self.schema_name().split('.')[-2]

    def code_field_name(self):
        return self.attr('meta.code_field_name', '{}_code'.format(self.object_name()))

    def name_field_name(self):
        return self.attr('meta.name_field_name', '{}_name'.format(self.object_name()))

    def is_column(self, property):
        return property.get('type') in column_types

    def is_relationship(self, property):
        return property['type'] == 'relation'

    def column_keys(self, sort=False):
        column_keys = [k for k, v in self.properties().items() if self.is_column(v)]
        if sort:
            column_keys.sort()
        return column_keys

    def relationship_keys(self):
        return [k for k, v in self.properties().items() if self.is_relationship(v)]

    def properties(self):
        return self.definition['properties']

    def property(self, key):
        return self.properties()[key]

    def columns(self, sort=False):

        column = {}

        for key in self.column_keys(sort=sort):
            column[key] = self.property(key)

        return column

    def relationships(self):

        relationship = {}
        for key in self.relationship_keys():
            relationship[key] = self.properties()[key]

        return relationship

    def column(self, key):
        return self.columns()[key]

    def relationship(self, key):
        return self.relationships()[key]

    def relation_type(self, relation_def):
        relation_type = (
            'n-1' if relation_def.get('local_key') and not relation_def.get('foreign_key')
            else '1-n' if relation_def.get('foreign_key') and not relation_def.get('local_key')
            else 'n-n' if relation_def.get('foreign_key') and relation_def.get('local_key')
            else None
        )

        if relation_type is None:
            raise SchemaRelationError('relation type is None for relation_def : {}'.format(relation_def))
        return relation_type

    def columns_array(self, columns_only=False):
        '''
            return properties as array

            store properties key as 'name'
        '''

        properties_dict = copy.deepcopy(self.columns())
        columns_array = []

        for k, v in properties_dict.items():
            v.update({'name': k})
            columns_array.append(v)

        return columns_array

    def dependencies(self, exclude_deps=[]):
        deps = [self.schema_name()]
        for key, relation_def in self.relationships().items():
            schema_name = relation_def['schema_name']

            if schema_name in deps + exclude_deps:
                continue

            deps.append(schema_name)
            deps += (
                self.cls(relation_def['schema_name'])
                .dependencies(exclude_deps=deps + exclude_deps)
            )

        if self.schema_name() in deps:
            deps.remove(self.schema_name())

        return list(dict.fromkeys(deps))