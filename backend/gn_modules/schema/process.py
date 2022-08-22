'''
    process definition_schema for
    - validation
    - schema ajsf
'''

import copy

class SchemaProcess():

    @classmethod
    def defs_id(cls, schema_name):
        return schema_name.replace('.', '_')


    def set_definition(self, definitions, schema_name, schema):

        schema_definition_id = self.cls.defs_id(schema_name)

        schema_definition = {}

        dependencies = []

        # patch oneOf ne marche pas avec ajsf
        if schema_name == 'references.geom.geometry':
            dependencies = [
                'references.geom.point',
                'references.geom.multilinestring',
                'references.geom.polygon',
            ]

        for key, definition in schema.get('definitions', {}).items():
            if key == schema_name:
                continue

            dependencies.append(key)

            if key in definitions:
                continue

            definitions[key] = definition

        # type_object = 'object'
        # type_object = (
        #     ['object', 'null'] if is_validation_schema
        #     else 'object'
        # )

        schema_definition = {
            'type': 'object',
        }

        if 'properties' in schema:
            schema_definition['properties'] = schema['properties']

        # if is_validation_schema:
        # schema_definition = {
        #     'oneOf': [
        #         {'type': 'null'},
        #         schema_definition
        #     ]
        # }

        schema_definition['deps'] = dependencies
        schema_definition = self.process_json_schema(schema_definition)

        definitions[schema_definition_id] = schema_definition

        self.set_global_cache('js_definition', schema_definition_id, schema_definition)

    def set_definition_from_schema_name(self, definitions, schema_name):
        '''
        '''
        schema_definition_id = self.cls.defs_id(schema_name)

        if schema_definition_id in definitions:
            return

        if schema_definition :=self.get_global_cache('js_definition', schema_definition_id):
            definitions[schema_definition_id] = schema_definition
            deps = schema_definition['deps']
            for dep in deps:
                self.set_definition_from_schema_name(definitions, dep)
            return

        if 'references' in schema_name:
            definition = self.get_global_cache('reference', schema_name.split('.')[-1])
        else:
            relation = self.cls(schema_name)
            definition = copy.deepcopy(relation.get_schema(columns_only=True))

        self.set_definition(definitions, schema_name, definition)


    def get_json_schema(self):
        '''
            - put references into definitions
        '''

        # references & definitions
        properties = {}
        definitions = {}

        # - colonnes
        for key, _column_def in self.columns().items():
            column_def = copy.deepcopy(_column_def)
            if column_def['type'] == 'geometry':
                schema_name = 'references.geom.{}'.format(column_def['geometry_type'])
                self.set_definition_from_schema_name(definitions, schema_name)
                column_def['$ref'] = '#/definitions/{}'.format(self.cls.defs_id(schema_name))
                column_def.pop('type')

            properties[key] = self.process_json_schema(column_def)

        processed_schema = {
            # '$id': self.id(),
            'type': 'object',
            'required': self.required(),
            'definitions': definitions,
            'properties': properties
        }

        # avoid circular deps
        # self.cls.set_global_cache(
        #     'js_definition',
        #     self.schema_name(),
        #     copy.deepcopy(processed_schema)
        # )

        self.set_definition(
            self.cls.get_global_cache('js_definition'),
            self.schema_name(),
            copy.deepcopy(processed_schema)
        )

        # - relations
        for key, _relation_def in self.relationships().items():
            relation_def = copy.deepcopy(_relation_def)
            relation_def.pop('type')
            self.set_definition_from_schema_name(definitions, relation_def['schema_name'])

            properties[key] = self.process_json_schema(
                relation_def
            )

            ref = '#/definitions/{}'.format(self.cls.defs_id(relation_def['schema_name']))

            # relation 1 n
            if relation_def['relation_type'] == 'n-1':
                properties[key]['$ref'] = ref

            if relation_def['relation_type'] == '1-n':

                properties[key]['type'] = 'array'
                properties[key]['items'] = {'$ref': ref}
                properties[key] = {
                    'oneOf': [
                        {'type': 'null'},
                        properties[key]
                    ]
                }

            if relation_def['relation_type'] == 'n-n':
                properties[key]['type'] = 'array'
                properties[key]['items'] = {'$ref': ref}
                properties[key] = {
                    'oneOf': [
                        {'type': 'null'},
                        properties[key]
                    ]
                }

        self.set_definition(
            self.cls.get_global_cache('js_definition'),
            self.schema_name(),
            copy.deepcopy(processed_schema)
        )

        return processed_schema

    def process_json_schema(self, schema):
        '''
            create validation schema from schema to accept None in case of
                number
                string

            exemple : 'number' => ['number', 'null']
        '''

        if type(schema) is list:
            return [self.process_json_schema(elem) for elem in schema]

        if type(schema) is dict:

            if schema.get('type') in ['date', 'datetime', 'uuid']:
                schema['format'] = schema.get('format', schema.get('type'))
                schema['type'] = 'string'

            if schema.get('type') == 'json':
                schema['type'] = 'object'

            return {key: self.process_json_schema(elem) for key, elem in schema.items() if key != 'required'}

        return schema



    def process_validation_schema(self, schema, key=None):
        '''
            create validation schema from schema to accept None in case of
                number
                string

            exemple : 'number' => ['number', 'null']
        '''

        if type(schema) is list:
            return [self.process_validation_schema(elem, key) for elem in schema]

        if type(schema) is dict:

            if (
                schema.get('type') in ['number', 'string', 'integer', 'boolean']
                and key and not self.is_required(key)
            ):
                schema['type'] = [schema['type'], 'null']
            else:
                return {key: self.process_validation_schema(elem, key) for key, elem in schema.items()}

        return schema
