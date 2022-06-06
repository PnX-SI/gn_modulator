'''
    SchemaMethods : sqlalchemy existing_Models processing
'''

import uuid

from flask_sqlalchemy import model
from geoalchemy2 import Geometry
from gn_modules.schema.repositories import cruved

from sqlalchemy.orm import column_property

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, select, case, exists, and_ , literal_column, cast, column
from sqlalchemy.dialects.postgresql import aggregate_order_by

from geonature.utils.env import db

from ..errors import SchemaProcessedPropertyError

# store the sqla Models

class SchemaModelBase():
    '''
        sqlalchemy Models processing
    '''

    def model_name(self):
        '''
        '''

        return self.attr('meta.model_name', 'T{}'.format(self.schema_name('pascal_case')))

    def get_db_type(self, column):

        field_type = column.get('type')

        if field_type == 'integer':
            return db.Integer
        if field_type == 'boolean':
            return db.Boolean
        if field_type == 'number':
            return db.Float
        if field_type == 'string':
            return db.Unicode
        if field_type == 'uuid':
            return UUID(as_uuid=True)
        if field_type == 'date':
            return db.Date
        if field_type == 'datetime':
            return db.DateTime
        if field_type == 'geometry':
            return Geometry(column['geometry_type'], column['srid'])

        raise(
            SchemaProcessedPropertyError(
                'db_type is None for prop {}'
                .format(column)
            )
        )

    def process_existing_column_model(self, key, column_def, column_model):
        pass

    def process_column_model(self, column_def):
        '''
        '''
        # get field_options
        field_args = []
        field_kwargs = {}
        db_type = None

        # primary key
        if column_def.get('primary_key'):
            field_kwargs['primary_key'] = True

        # foreign_key
        if column_def.get('foreign_key'):
            relation = self.cls(column_def['schema_name'])
            foreign_key = '{}.{}'.format(relation.sql_schema_dot_table(), relation.pk_field_name())
            field_args.append(db.ForeignKey(foreign_key))

        # process type
        db_type = self.get_db_type(column_def)

        # default
        if column_def.get('default'):
            field_kwargs['default'] = self.process_default_model(column_def)

        return db.Column(db_type, *field_args, **field_kwargs)

    def process_default_model(self, column_def):
        if column_def['type'] == 'uuid':
            return uuid.uuid4

    def process_relation_model(self, key, relationship_def, Model):

        relation = self.cls(relationship_def['schema_name'])

        kwargs = {}
        if relationship_def.get('relation_type') == '1-1':
            kwargs['uselist'] = False

        if relationship_def.get('relation_type') == 'n-1':
            kwargs['foreign_keys'] = getattr(Model, relationship_def['local_key'])

            # patch si la cle n'est pas definie
            column_def = self.column(relationship_def['local_key'])
            relation = self.cls(column_def['schema_name'])

            kwargs['primaryjoin'] = (
                getattr(self.Model(), relationship_def['local_key'])
                ==
                getattr(relation.Model(), relation.pk_field_name())
            )

        if relationship_def.get('relation_type') == 'n-n':
            kwargs['secondary'] = self.CorTable(relationship_def)

        # kwargs['lazy'] = 'joined'

        relationship = db.relationship(relation.Model(), **kwargs)

        return relationship

    def CorTable(self, relation_def):

        schema_dot_table = relation_def.get('schema_dot_table')
        cor_schema_name = schema_dot_table.split('.')[0]
        cor_table_name = schema_dot_table.split('.')[1]

        CorTable = self.cls.get_global_cache(
            'cor_table',
            schema_dot_table
        )
        if CorTable is not None:
            return CorTable

        relation = self.cls(relation_def['schema_name'])
        local_key = self.pk_field_name()
        foreign_key = relation.pk_field_name()

        CorTable = db.Table(
            cor_table_name,
            db.metadata,
            db.Column(
                local_key,
                db.ForeignKey('{}.{}'.format(self.sql_schema_dot_table(), local_key)),
                primary_key=True
            ),
            db.Column(
                foreign_key,
                db.ForeignKey('{}.{}'.format(relation.sql_schema_dot_table(), foreign_key)),
                primary_key=True
            ),
            schema=cor_schema_name
        )

        self.cls.set_global_cache('cor_table', schema_dot_table, CorTable)

        return CorTable

    def Model(self):
        if not self.sql_table_exists():
            return None
        '''
        create and returns schema Model : a class created with type(name, (bases,), dict_model) function
        - name : self.model_name()
        - base :  db.Model
        - dict_model : contains properties and methods

        TODO store in global variable and create only if missing
        - avoid to create the model twice
        '''
        # get Model from cache
        if Model := self.cls.get_schema_cache(self.schema_name(), 'model'):
            return Model

        # get Model from existing
        if Model := self.get_existing_model():
            return Model

        # dict_model used with type() to list properties and methods for class creation
        dict_model = {
            '__tablename__': self.sql_table_name(),
            '__table_args__': {
                'schema': self.sql_schema_name(),
            }
        }

        ModelBaseClass = db.Model
        if self.attr('meta.extends'):
            dict_model['__mapper_args__'] = {
                'polymorphic_identity': self.attr('meta.extends.type'),
            }
            base_schema = self.cls(self.attr('meta.extends.schema_name'))
            ModelBaseClass = base_schema.Model()

        if self.attr('meta.extends'):
            base_schema = self.cls(self.attr('meta.extends.schema_name'))

        # process properties
        for key, column_def in self.columns().items():

            if column_def.get('column_property') is not None:
                continue

            if self.attr('meta.extends'):
                base_schema = self.cls(self.attr('meta.extends.schema_name'))
                if key in base_schema.column_keys() and key != base_schema.pk_field_name():
                    continue

            dict_model[key] = self.process_column_model(column_def)

        Model = type(self.model_name(), (ModelBaseClass,), dict_model)

        # store in cache before relations (avoid circular dependancies)
        self.cls.set_schema_cache(self.schema_name(), 'model', Model)

        # process relations

        for key, relationship_def in self.relationships().items():
            if self.attr('meta.extends'):
                base_schema = self.cls(self.attr('meta.extends.schema_name'))
                if key in base_schema.column_keys():
                    continue

            relationship = self.process_relation_model(key, relationship_def, Model)
            setattr(Model, key, relationship)

        # process column properties

        for type_column_property in [
            'nb',
            'has',
            'label',
            'st_x',
            'st_y',
            'type_complement'
        ]:
            for key, column_property_def in self.columns().items():
                if column_property_def.get('column_property') != type_column_property:
                    continue

                setattr(Model, key, self.process_column_property_model(key, column_property_def, Model))

        return Model
