'''
    SchemaMethods : sqlalchemy existing_Models processing
'''

from geoalchemy2 import Geometry

from sqlalchemy.orm import column_property

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, select

from geonature.utils.env import DB

from .errors import SchemaProcessedPropertyError

from geonature.core.taxonomie.models import Taxref  # noqa
from geonature.core.gn_synthese.models import Synthese  # noqa
from geonature.core.gn_meta.models import TDatasets  # noqa
from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes # noqa
from geonature.core.ref_geo.models import LAreas, BibAreasTypes

# store the sqla Models
cache_model = {}
cache_cor_table = {}


class SchemaModel():
    '''
        sqlalchemy Models processing
    '''

    @classmethod
    def c_get_model_from_schema_dot_table(cls, schema_dot_table):
        for Model in DB.Model._decl_class_registry.values():
            if not (isinstance(Model, type) and issubclass(Model, DB.Model)):
                continue

            sql_table_name = Model.__tablename__
            sql_schema_name = Model.__table__.schema

            if '{}.{}'.format(sql_schema_name, sql_table_name) == schema_dot_table:
                return Model

    # def existing_Models(self):
    #     existing_Models = {}

    #     for cls in DB.Model._decl_class_registry.values():
    #         if isinstance(cls, type) and issubclass(cls, DB.Model):
    #             d = cls.__table_args__
    #             if type(cls.__table_args__) is tuple:
    #                 for elem in d:
    #                     if 'schema' in elem:
    #                         schema = elem['schema']
    #             else:
    #                 schema = cls.__table_args__['schema']

    #             key = '{}.{}'.format(schema, cls.__tablename__)
    #             # if key in existing_Models:
    #             #     continue
    #             # existing_Models[key] = cls

    #     return existing_Models

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
            return DB.Integer
        if field_type == 'boolean':
            return DB.Boolean
        if field_type == 'number':
            return DB.Float
        if field_type == 'string':
            return DB.Unicode
        if field_type == 'uuid':
            return UUID
        if field_type == 'date':
            return DB.Date
        if field_type == 'datetime':
            return DB.DateTime
        if field_type == 'geometry':
            return Geometry(column['geometry_type'], column['srid'])

        raise(
            SchemaProcessedPropertyError(
                'db_type is None for prop {}'
                .format(column)
            )
        )

    def process_existing_column_model(self, key, column_def, column_model):
        if self.get_foreign_key(column_def) and not column_model.foreign_keys:
            # print(dir(column_model.parent))
            # print(column_model.parent)
            # relation_name, foreign_key_field_name = self.parse_foreign_key(self.get_foreign_key(column_def))
            # relation = self.cls()(relation_name)
            # foreign_key = '{}.{}'.format(relation.schema_dot_table(), foreign_key_field_name)
            # # column_model.foreign_keys = DB.ForeignKey(foreign_key)
            # column_model.parent.c.ForeignKeyConstraint((key,), ['{}.{}'.format(relation.schema_dot_table(), foreign_key)])

            # print(column_model.foreign_keys)

            # TODO how to dynamically set a foreign key constraint
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
        if self.get_foreign_key(column_def):
            relation_name, foreign_key_field_name = self.parse_foreign_key(self.get_foreign_key(column_def))
            relation = self.cls()(relation_name)
            foreign_key = '{}.{}'.format(relation.schema_dot_table(), foreign_key_field_name)
            field_args.append(DB.ForeignKey(foreign_key))

        # process type
        db_type = self.get_db_type(column_def)

        return DB.Column(db_type, *field_args, **field_kwargs)

    def process_relation_model(self, key, relationship_def, Model):

        relation = self.cls()(relationship_def['rel'])

        kwargs = {}
        if self.relation_type(relationship_def) == 'n-1':
            kwargs['foreign_keys'] = getattr(Model, relationship_def['local_key'])

            # patch si la cle n'est pas definie
            column_def = self.column(relationship_def['local_key'])
            relation_name, foreign_key_field_name = self.parse_foreign_key(self.get_foreign_key(column_def))

            kwargs['primaryjoin'] = (
                getattr(self.Model(), relationship_def['local_key'])
                ==
                getattr(self.cls()(relation_name).Model(), foreign_key_field_name)
            )

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
        Model = None
        # Model = self.existing_Models()[self.schema_dot_table()]
        for Model_ in DB.Model._decl_class_registry.values():
            if isinstance(Model_, type) and issubclass(Model_, DB.Model):
                if self.model_name() == Model_.__name__:
                    Model = Model_
                    # break

        if not Model:
            return None

        for key, column_def in self.columns().items():
            if hasattr(Model, key):
                self.process_existing_column_model(key, column_def, getattr(Model, key))
                # continue
            else:
                setattr(Model, key, self.process_column_model(column_def))

        # store in cache before relation (avoid circular dependancies)
        cache_model[self.schema_name()] = Model

        for key, relation_def in self.relationships().items():
            if hasattr(Model, key):
                continue

            setattr(Model, key, self.process_relation_model(key, relation_def, Model))

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

        if Model := self.get_existing_model():
            return Model

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
            setattr(Model, key, self.process_relation_model(key, value, Model))

        return Model
