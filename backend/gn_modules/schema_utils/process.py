'''
    process raw_schema for
    - validation
    - schema ajsf
'''

import copy

cache_definitions = {}

class SchemaProcess():

    @classmethod
    def defs_id(cls, schema_name):
        # return schema_name
        # return '/{}'.format(schema_name.replace('.', '/'))
        return schema_name.replace('.', '_')

    def set_definition(self, definitions, schema_name, schema):

        schema_definition_id = self.cls().defs_id(schema_name)

        dependencies = []
        for key, schema_definition in schema.get('definitions', {}).items():
            if key == schema_name:
                continue
            dependencies.append(key)

            if key in definitions:
                continue

            definitions[key] = schema_definition

        definitions[schema_definition_id] = {
            'type': 'object',
            # '$id': schema_definition_id,
            'deps': dependencies
        }

        if 'properties' in schema:
            definitions[schema_definition_id]['properties'] = schema['properties']
        if 'oneOf' in schema:
            definitions[schema_definition_id]['oneOf'] = schema['oneOf']

        cache_definitions[schema_definition_id] = self.validation_schema(definitions[schema_definition_id])

    def set_definition_from_schema_name(self, definitions, schema_name):
        '''
        '''
        schema_definition_id = self.cls().defs_id(schema_name)

        if schema_definition_id in definitions:
            return

        if schema_definition_id in cache_definitions:
            definitions[schema_definition_id] = cache_definitions[schema_definition_id]
            for dep in cache_definitions[schema_definition_id]['deps']:
                self.set_definition_from_schema_name(definitions, dep)
            return

        if 'references' in schema_name:
            schema = self.cls().load_json_file_from_name(schema_name)
        if 'schemas' in schema_name:
            relation = self.cls()(schema_name)
            # column only ??
            schema = relation.processed_schema(columns_only=True)

        self.set_definition(definitions, schema_name, schema)


    def process_raw_schema(self):
        '''
            - put references into definitions
        '''

        # references & definitions
        properties = {}
        definitions = {}

        # - colonnes
        for key, _column_def in self.columns().items():
            column_def = copy.deepcopy(_column_def)
            if self.is_geometry(column_def):
                schema_name = 'references.geom.{}'.format(column_def['geometry_type'])
                self.set_definition_from_schema_name(definitions, schema_name)
                column_def['$ref'] = '#/definitions/{}'.format(self.cls().defs_id(schema_name))

            properties[key] = self.validation_schema(column_def)

        processed_schema = {
            # '$id': self.id(),
            'type': 'object',
            'required': self.required(),
            'definitions': definitions,
            'properties': properties
        }

        # avoid circular deps
        self.set_definition(cache_definitions, self.schema_name(), copy.copy(processed_schema))

        # - relations
        for key, _relation_def in self.relationships().items():
            relation_def = copy.deepcopy(_relation_def)
            self.set_definition_from_schema_name(definitions, relation_def['rel'])
            properties[key] = self.validation_schema({
                **relation_def,
            })

            ref = '#/definitions/{}'.format(self.cls().defs_id(relation_def['rel']))

            # relation 1 n
            if self.relation_type(relation_def) == 'n-1':
                properties[key]['type'] = ['object', 'null']
                properties[key]['$ref'] = ref

            if self.relation_type(relation_def) == '1-n':
                properties[key]['type'] = 'array'
                properties[key]['items'] = {'$ref': ref}

            if self.relation_type(relation_def) == 'n-n':
                properties[key]['type'] = 'array'
                properties[key]['items'] = {'$ref': ref}

        self.set_definition(cache_definitions, self.schema_name(), processed_schema)

        return processed_schema
