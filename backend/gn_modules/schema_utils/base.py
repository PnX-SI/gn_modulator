'''
    SchemaMethods : base methods for schemas

    - setters, getters
    - utils - schema parser

'''

import copy
import json
import re

from geonature.utils.config import config

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

    def cls(self):
        '''
            Renvoie la classe de l'object courant
        '''
        return self.__class__

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

    def schema(self, schema_type='raw', columns_only=False):

        if 'raw' not in self._schemas:
            self.reload()
        schema = self._schemas[schema_type]

        if columns_only:
            schema = copy.copy(schema)
            schema['properties'] = {
                key: column_def
                for key, column_def in schema['properties'].items()
                if key in self.column_keys()
            }
            return schema

        return schema

    # utils - schema parser

    def id(self):
        return self.schema()['$id']

    def required(self):
        return self.schema().get('required', [])

    def is_required(self, key):
        return self.properties()[key].get('required') or key in self.required()

    def meta(self, prop=None, default=None):
        '''
            renvoie
            - $meta si prop est null
            - $meta['prop1']['prop2']['prop3'] si prop = 'prop1.prop2.prop3'

            ou $meta.prop
        '''

        elem = self.schema()['$meta']

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

        if letter_case == 'pascal_case':
            return (
                self._schema_name
                    .replace('.', ' ')
                    .title()
                    .replace(' ', '')
            )
        if letter_case in ['snake_case', '_']:
            return self._schema_name.replace('.', '_')
        if letter_case == '/':
            return self._schema_name.replace('.', '/')
        else:
            return self._schema_name

    def pk_field_names(self):
        '''
            returns list of primary keys from self._raw_schema['properties']
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
        return self.meta('code_field_name', '{}_code'.format(self.object_name()))

    def name_field_name(self):
        return self.meta('name_field_name', '{}_name'.format(self.object_name()))

    def is_column(self, property):
        return property.get('type') in column_types

    def is_relationship(self, property):
        return 'rel' in property

    def column_keys(self, sort=False):
        column_keys = [k for k, v in self.properties().items() if self.is_column(v)]
        if sort:
            column_keys.sort()
        return column_keys

    def relationship_keys(self):
        return [k for k, v in self.properties().items() if self.is_relationship(v)]

    def properties(self, schema_type='raw'):
        return self.schema(schema_type=schema_type)['properties']

    def get_property(self, key):
        schema = self.schema(schemea_type='validation')

        elem = schema['properties']

        key_parts = key.split('.')
        for idx, key_part in enumerate(key_parts):
            # cas des array
            if key_part.endswith('[]'):
                elem = elem[key_part.replace('[]', '')]
                if not elem['type'] == 'array':
                    raise Exception("Erreur clé {} ({}: {}  n'est pas de type array".format(key, key_part, elem))
                if idx == len(key_parts) - 1:
                    return elem
                elem = elem['items']

            elif key_part in elem:
                elem = elem[key_part]
            else:
                raise Exception("Erreur clé {} ({} pour {})".format(key, key_part, elem))

            if '$ref' in elem:
                definition_key = elem['$ref'].split('/')[-1]
                elem = {
                    **elem,
                    **schema['definitions'][definition_key]['properties']
                }
                elem.pop('$ref')

        return elem

    def columns(self, schema_type='raw', sort=False):

        column = {}

        for key in self.column_keys(sort=sort):
            column[key] = self.properties(schema_type)[key]

        return column

    def relationships(self, schema_type='raw'):

        relationship = {}
        for key in self.relationship_keys():
            relationship[key] = self.properties(schema_type)[key]

        return relationship

    def column(self, key, schema_type='raw'):
        return self.columns(schema_type)[key]

    def relationship(self, key, schema_type='raw'):
        return self.relationships(schema_type)[key]

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

        properties_dict = copy.copy(self.columns())
        columns_array = []

        for k, v in properties_dict.items():
            v.update({'name': k})
            columns_array.append(v)

        return columns_array

    def parse_foreign_key(self, foreign_key):
        '''
            renvoie la reference de l'object de la clé étrangère ainsi que le nom du champs de clé étrangère
        '''

        schema_ref, fk_field_name = tuple(foreign_key.split('.'))
        schema_name = schema_ref.replace('/', '.')
        return schema_name, fk_field_name

    def get_foreign_key(self, prop):
        '''
            renvoie la référence de la clé étrangère
        '''

        if prop.get('nomenclature_type'):
            return 'schemas/utils/nomenclature.id_nomenclature'

        return prop.get('foreign_key')

    def get_relation_from_foreign_key(self, foreign_key):
        relation_name, _ = self .parse_foreign_key(foreign_key)
        return self.cls()(relation_name)


    @classmethod
    def process_schema_config(cls, data, key=None):
        '''
            transforme les element commençant par '__CONFIG.' par leur valeur correspondante dans
            app.config

            par exemple __CONFIG.LOCAL_SRID =>
        '''

        # optimisation regexp

        if not hasattr(cls, '_re_CONFIG'):
            setattr(cls, '_re_CONFIG', re.compile(r'__CONFIG\.(.*?)__'))

        # process dict

        if type(data) is dict:
            return {
                k: cls.process_schema_config(v, k)
                for k, v in data.items()
            }

        # process list
        if type(data) is list:
            return [cls.process_schema_config(v) for v in data]

        # process text

        if type(data) is str and '__CONFIG.' in data:
            config_key_str = cls._re_CONFIG.search(data)
            config_key_str = config_key_str and config_key_str.group(1)

            if not config_key_str:
                return data

            config_keys = config_key_str.split('.')
            config_value = config
            try:
                for config_key in config_keys:
                    config_value = config_value[config_key]
            except Exception:
                raise SchemaProcessConfigError("La clé {} n'est pas dans la config de geonature".format(config_key_str))

            data = data.replace(data, str(config_value) or '')
            if key == 'srid':
                data = int(data)

        return data
