'''
    process raw_schema for
    - validation
    - schema ajsf
'''

import copy

cache_definitions = {
    'validation': {},
    'form': {}
}
class SchemaProcess():

    @classmethod
    def defs_id(cls, schema_name):
        # return schema_name
        # return '/{}'.format(schema_name.replace('.', '/'))
        return schema_name.replace('.', '_')

    def cache_definitions(self, is_validation_schema):
        return cache_definitions['validation' if is_validation_schema else 'form']

    def set_definition(self, definitions, schema_name, schema, is_validation_schema):

        schema_definition_id = self.cls().defs_id(schema_name)

        schema_definition = {}

        dependencies = []

        for key, definition in schema.get('definitions', {}).items():
            if key == schema_name:
                continue

            dependencies.append(key)

            if key in definitions:
                continue

            definitions[key] = definition

        type_object = (
            ['object', 'null'] if is_validation_schema
            else 'object'
        )

        schema_definition = {
            'type': 'object',
            # 'nullable': True
            # 'type': type_object
        }

        if 'properties' in schema:
            schema_definition['properties'] = schema['properties']

        # if 'oneOf' in schema:
            # schema_definition['oneOf'] = schema['oneOf']

        if is_validation_schema:
            schema_definition = {
                'oneOf': [
                    {'type': 'null'},
                    schema_definition
                ]
            }

        schema_definition['deps'] = dependencies
        schema_definition = self.validation_schema(schema_definition)

        definitions[schema_definition_id] = schema_definition
        self.cache_definitions(is_validation_schema)[schema_definition_id] = schema_definition

    def set_definition_from_schema_name(self, definitions, schema_name, is_validation_schema):
        '''
        '''
        schema_definition_id = self.cls().defs_id(schema_name)

        if schema_definition_id in definitions:
            return

        if schema_definition_id in self.cache_definitions(is_validation_schema):
            definitions[schema_definition_id] = self.cache_definitions(is_validation_schema)[schema_definition_id]

            deps = self.cache_definitions(is_validation_schema)[schema_definition_id]['deps']
            for dep in deps:
                self.set_definition_from_schema_name(definitions, dep, is_validation_schema)
            return

        if 'references' in schema_name:
            schema = self.cls().load_json_file_from_name(schema_name)
        if 'schemas' in schema_name:
            relation = self.cls()(schema_name)
            # column only ??
            schema = relation.schema('validation', columns_only=True)

        self.set_definition(definitions, schema_name, schema, is_validation_schema)


    def process_raw_schema(self, is_validation_schema):
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
                self.set_definition_from_schema_name(definitions, schema_name, is_validation_schema)
                column_def['$ref'] = '#/definitions/{}'.format(self.cls().defs_id(schema_name))
                column_def.pop('type')

            properties[key] = self.validation_schema(column_def)

        processed_schema = {
            # '$id': self.id(),
            'type': 'object',
            'required': self.required(),
            'definitions': definitions,
            'properties': properties
        }

        # avoid circular deps
        self.set_definition(self.cache_definitions(is_validation_schema), self.schema_name(), copy.copy(processed_schema), is_validation_schema)

        # - relations
        for key, _relation_def in self.relationships().items():
            relation_def = copy.deepcopy(_relation_def)
            self.set_definition_from_schema_name(definitions, relation_def['rel'], is_validation_schema)
            properties[key] = self.validation_schema({
                **relation_def,
            })

            ref = '#/definitions/{}'.format(self.cls().defs_id(relation_def['rel']))

            # relation 1 n
            if self.relation_type(relation_def) == 'n-1':
                if is_validation_schema:
                    # properties[key]['anyOf'] = [
                        # {'type': 'object'},
                        # {'type': 'null'},
                    # ]
                    properties[key]['$ref'] = ref
                    # properties[key]['type'] = 'null'
                else:
                    # properties[key]['type'] = 'object'
                    properties[key]['$ref'] = ref
                    # properties[key]['type'] = ['object', 'null']
                # properties[key]['nullable'] = True

            if self.relation_type(relation_def) == '1-n':
                properties[key]['type'] = 'array'
                properties[key]['items'] = {'$ref': ref}

            if self.relation_type(relation_def) == 'n-n':
                properties[key]['type'] = 'array'
                properties[key]['items'] = {'$ref': ref}

        self.set_definition(self.cache_definitions(is_validation_schema), self.schema_name(), processed_schema, is_validation_schema)

        return processed_schema
