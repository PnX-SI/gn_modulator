'''
    SchemaMethods : sqlalchemy existing_Models processing
'''

from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID

from geonature.utils.env import DB

from .errors import SchemaProcessedPropertyError

from geonature.core.taxonomie.models import Taxref # noqa
from geonature.core.gn_synthese.models import Synthese # noqa


# store the sqla Models
cache_model = {}
cache_cor_table = {}


class SchemaModel():
    '''
        sqlalchemy Models processing
    '''

    def existing_Models(self):

        existing_Models = {}

        for cls in DB.Model._decl_class_registry.values():
            if isinstance(cls, type) and issubclass(cls, DB.Model):
                d = cls.__table_args__
                if type(cls.__table_args__) is tuple:
                    for elem in d:
                        if 'schema' in elem:
                            schema = elem['schema']
                else:
                    schema = cls.__table_args__['schema']

                key = '{}.{}'.format(schema, cls.__tablename__)
                existing_Models[key] = cls

        return existing_Models

    def model_name(self):
        '''
        '''

        return self.meta('model_name', 'T{}'.format(self.schema_name('pascal_case')))

    def clear_cache_model(self):
        if cache_model.get(self.schema_name()):
            del cache_model[self.schema_name()]

    def get_db_type(self, column):

        field_type = column.get('type')

        if field_type == 'integer':
            db_type = DB.Integer
        elif field_type == 'number':
            db_type = DB.Float
        elif field_type == 'string':
            if column.get('format') == 'uuid':
                db_type = UUID
            else:
                db_type = DB.Unicode
        elif field_type == 'date':
            db_type = DB.DateTime
        elif self.is_geometry(column):
            db_type = Geometry(column['geometry_type'], column['srid'])

        if not db_type:
            raise(
                SchemaProcessedPropertyError(
                    'db_type is None for prop {}'
                    .format(column)
                )
            )

        return db_type

    def process_column_model(self, column):
        '''
        '''

        # get field_options
        field_args = []
        field_kwargs = {}
        db_type = None

        # primary key
        if column.get('primary_key'):
            field_kwargs['primary_key'] = True

        # foreign_key
        if self.get_foreign_key(column):
            relation_name, foreign_key_field_name = self.parse_foreign_key(self.get_foreign_key(column))
            relation = self.cls()(relation_name)
            foreign_key = '{}.{}'.format(relation.schema_dot_table(), foreign_key_field_name)
            field_args.append(DB.ForeignKey(foreign_key))

        # process type
        db_type = self.get_db_type(column)

        return DB.Column(db_type, *field_args, **field_kwargs)

    def process_relation_model(self, relationship_def, Model):

        relation = self.cls()(relationship_def['rel'])

        kwargs = {}
        if self.relation_type(relationship_def) == 'n-1':
            kwargs['foreign_keys'] = getattr(Model, relationship_def['local_key'])
        if self.relation_type(relationship_def) == 'n-n':
            kwargs['secondary'] = self.CorTable(relationship_def)

        return DB.relationship(relation.Model(), **kwargs)

    def CorTable(self, relation_def):

        cor_schema_dot_table = self.cor_schema_dot_table(relation_def)
        cor_schema_name = self.cor_schema_name(relation_def)
        cor_table_name = self.cor_table_name(relation_def)

        if cache_cor_table.get(cor_schema_dot_table):
            return cache_cor_table[cor_schema_dot_table]

        relation = self.cls()(relation_def['rel'])

        CorTable = DB.Table(
            cor_table_name,
            DB.metadata,
            DB.Column(
                relation_def['local_key'],
                DB.ForeignKey('{}.{}'.format(self.schema_dot_table(), relation_def['local_key']))
            ),
            DB.Column(
                relation_def['foreign_key'],
                DB.ForeignKey('{}.{}'.format(relation.schema_dot_table(), relation_def['foreign_key']))
            ),
            schema=cor_schema_name
        )

        cache_cor_table[cor_schema_dot_table] = CorTable

        return CorTable

    def get_existing_model(self):
        '''
        '''

        Model = self.existing_Models()[self.schema_dot_table()]

        for key, column_def in self.columns().items():
            if hasattr(Model, key):
                continue
            setattr(Model, key, self.process_column_model(column_def))

        # store in cache before relation (avoid circular dependancies)
        cache_model[self.schema_name()] = Model

        for key, relation_def in self.relationships().items():
            if hasattr(Model, key):
                continue
            setattr(Model, key, self.process_relation_model(relation_def, Model))

        return Model

    def Model(self):
        '''
        create and returns schema Model : a class created with type(name, (bases,), dict_model) function
        - name : self.model_name()
        - base :  DB.Model
        - dict_model : contains properties and methods

        TODO store in global variable and create only if missing
        - avoid to create the model twice
        '''
        # get Model from cache
        if Model := cache_model.get(self.schema_name()):
            return Model

        if self.schema_dot_table() in self.existing_Models():
            Model = self.get_existing_model()

        else:
            # dict_model used with type() to list properties and methods for class creation
            dict_model = {
                '__tablename__': self.sql_table_name(),
                '__table_args__': {
                    'schema': self.sql_schema_name(),
                }
            }

            # process properties
            for key, column_def in self.columns().items():
                dict_model[key] = self.process_column_model(column_def)

            Model = type(self.model_name(), (DB.Model,), dict_model)

            # store in cache before relations (avoid circular dependancies)
            cache_model[self.schema_name()] = Model

            # process relations
            for key, value in self.relationships().items():
                setattr(Model, key, self.process_relation_model(value, Model))

        return Model
