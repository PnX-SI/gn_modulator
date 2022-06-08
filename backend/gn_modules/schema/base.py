'''
    SchemaMethods : base methods for schemas

    - setters, getters
    - utils - schema parser

'''

from cProfile import label
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
        return self.attr("required", [])

    def is_required(self, key):

        return (
            key in self.properties()
            and (
                self.properties()[key].get('required')
                or key in self.required()
                or key in self.pk_field_names()
            )
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

    def is_column(self, key):
        return self.has_property(key) and self.property(key).get('type') in column_types

    def is_column_property(self, key):
        return (
            self.has_property(key)
            and self.property(key).get('type') in column_types
            and self.property(key).get('column_property')
        )

    def is_relationship(self, key):
        return  self.has_property(key) and self.property(key)['type'] == 'relation'

    def column_keys(self, sort=False):
        column_keys = [k for k, v in self.properties().items() if self.is_column(k)]
        if sort:
            column_keys.sort()
        return column_keys

    def column_properties_keys(self, sort=False):
        column_keys = [k for k, v in self.properties().items() if self.is_column_property(k)]
        if sort:
            column_keys.sort()
        return column_keys


    def relationship_keys(self):
        return [k for k, v in self.properties().items() if self.is_relationship(k)]

    def properties(self):
        return self.definition['properties']

    def property(self, key):

        if '.' in key:
            # on cherche la relation
            rel_key = key.split('.')[0]
            rel_prop = self.property(rel_key)
            rel = self.cls(rel_prop['schema_name'])
            return rel.property(key.split('.')[1])
        return self.properties()[key]

    def has_property(self, key):
        if '.' in key:
            # on cherche la relation
            rel_key = key.split('.')[0]
            if not self.has_property(rel_key):
                return False
            rel_prop = self.property(rel_key)
            rel = self.cls(rel_prop['schema_name'])
            return rel.has_property(key.split('.')[1])
        return self.properties().get(key) is not None

    def columns(self, sort=False):

        column = {}

        for key in self.column_keys(sort=sort):
            column[key] = self.property(key)

        return column

    def column_properties(self, sort=False):

        column = {}

        for key in self.column_properties_keys(sort=sort):
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

    def remove_field(self, field_name, schema):

        if isinstance(schema, dict):
            schema_out = {}
            for k, v in schema.items():
                if k == field_name:
                    continue
                schema_out[k] = self.remove_field(field_name, v)
            return schema_out

        if isinstance(schema, list):
            return [self.remove_field(field_name, v) for v in schema]

        return schema


    ## A mettre ailleurs


    def process_csv_keys(self, keys):
        return [
            self.property(key.split('.')[0])['title'] if self.has_property(key.split('.')[0])
            else key
            for key in keys
        ]

    def process_csv_data(self, key, data, options={}):
        """
        pour rendre les sorties des relations jolies pour l'export ??
        """

        if isinstance(data, list):
            return ", ".join([self.process_csv_data(key, d) for d in data])

        if isinstance(data, dict):

            if not key:
                return "_".join([self.process_csv_data(None, data[k]) for k in data.keys()])

            if '.' in key:
                key1 = key.split('.')[0]
                key2 = '.'.join(key.split('.')[1:])

                return self.process_csv_data(key2, data[key1])


            options = self.has_property(key) and self.property(key) or {}
            return self.process_csv_data(None, data[key], options)

        if labels:=options.get('labels'):

            if data is True:
                return labels[0] if len(labels) > 0 else True
            elif data is False:
                return labels[1] if len(labels) > 1 else False
            else:
                return labels[1] if len(labels) > 2 else None

        return data