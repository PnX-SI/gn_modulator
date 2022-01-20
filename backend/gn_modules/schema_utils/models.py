'''
    SchemaMethods : sqlalchemy existing_Models processing
'''

from flask_sqlalchemy import model
from geoalchemy2 import Geometry
from gn_modules.schema_utils.repositories import cruved

from sqlalchemy.orm import column_property

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, select, case, exists, and_ , literal_column, cast
from sqlalchemy.dialects.postgresql import aggregate_order_by

from geonature.utils.env import DB

from .errors import SchemaProcessedPropertyError

# store the sqla Models


from geonature.core.taxonomie.models import Taxref  # noqa
from geonature.core.gn_synthese.models import Synthese  # noqa
from geonature.core.gn_meta.models import TDatasets  # noqa
from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes # noqa
from geonature.core.ref_geo.models import LAreas, BibAreasTypes # noqa
from pypnusershub.db.models import User, Organisme # noqa
from geonature.core.users.models import CorRole # noqa
from geonature.core.gn_commons.models.base import CorModuleDataset # noqa

cache_model = {
    # 'schemas.utils.commons.module_jdd': CorModuleDataset
}

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
        if cache_model.get(self.schema_name()) is not None:
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
            relation = self.cls()(column_def['schema_name'])
            foreign_key = '{}.{}'.format(relation.schema_dot_table(), relation.pk_field_name())
            field_args.append(DB.ForeignKey(foreign_key))

        # process type
        db_type = self.get_db_type(column_def)

        return DB.Column(db_type, *field_args, **field_kwargs)

    def process_relation_model(self, key, relationship_def, Model):

        relation = self.cls()(relationship_def['schema_name'])

        kwargs = {}
        if relationship_def.get('relation_type') == 'n-1':
            kwargs['foreign_keys'] = getattr(Model, relationship_def['local_key'])

            # patch si la cle n'est pas definie
            column_def = self.column(relationship_def['local_key'])
            relation = self.cls()(column_def['schema_name'])

            kwargs['primaryjoin'] = (
                getattr(self.Model(), relationship_def['local_key'])
                ==
                getattr(relation.Model(), relation.pk_field_name())
            )

        if relationship_def.get('relation_type') == 'n-n':
            kwargs['secondary'] = self.CorTable(relationship_def)

        # kwargs['lazy'] = 'joined'

        relationship = DB.relationship(relation.Model(), **kwargs)

        return relationship

    def process_column_property_model(self, key, column_property_def, Model):
        print('cp', key)
        if column_property_def.get('column_property') == 'nb':

            return column_property(
                select([func.count('*')])
                .where(getattr(Model, column_property_def['relation_key']))
            )

        if column_property_def.get('column_property') == 'has':

            return column_property(
                exists()
                .where(getattr(Model, column_property_def['relation_key']))
            )

        if column_property_def.get('column_property') == 'label':

            relation = getattr(Model, column_property_def['relation_key'])
            relation_label = getattr(relation.mapper.entity, column_property_def['label_key'])
            return column_property(
                select([
                    func.string_agg(
                        cast(relation_label, DB.String),
                        literal_column("', '")
                    )
                ])
                .where(relation)
            )


    def CorTable(self, relation_def):

        schema_dot_table = relation_def.get('schema_dot_table')
        cor_schema_name = schema_dot_table.split('.')[0]
        cor_table_name = schema_dot_table.split('.')[1]

        if cache_cor_table.get(schema_dot_table) is not None:
            return cache_cor_table[schema_dot_table]

        relation = self.cls()(relation_def['schema_name'])
        local_key = self.pk_field_name()
        foreign_key = relation.pk_field_name()

        CorTable = DB.Table(
            cor_table_name,
            DB.metadata,
            DB.Column(
                local_key,
                DB.ForeignKey('{}.{}'.format(self.schema_dot_table(), local_key)),
                primary_key=True
            ),
            DB.Column(
                foreign_key,
                DB.ForeignKey('{}.{}'.format(relation.schema_dot_table(), foreign_key)),
                primary_key=True
            ),
            schema=cor_schema_name
        )

        cache_cor_table[schema_dot_table] = CorTable

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

        print('get model {}'.format(self.schema_name()))

        # dict_model used with type() to list properties and methods for class creation
        dict_model = {
            '__tablename__': self.sql_table_name(),
            '__table_args__': {
                'schema': self.sql_schema_name(),
            }
        }

        ModelBaseClass = DB.Model
        if self.meta('extends'):
            dict_model['__mapper_args__'] = {
                'polymorphic_identity': self.meta('extends.type'),
            }
            base_schema = self.cls()(self.meta('extends.schema_name'))
            ModelBaseClass = base_schema.Model()

        if self.meta('extends'):
            base_schema = self.cls()(self.meta('extends.schema_name'))

        # process properties
        for key, column_def in self.columns().items():

            if column_def.get('column_property') is not None:
                continue

            if self.meta('extends'):
                base_schema = self.cls()(self.meta('extends.schema_name'))
                if key in base_schema.column_keys() and key != base_schema.pk_field_name():
                    continue

            dict_model[key] = self.process_column_model(column_def)

        Model = type(self.model_name(), (ModelBaseClass,), dict_model)

        # store in cache before relations (avoid circular dependancies)
        cache_model[self.schema_name()] = Model

        # process relations
        for key, relationship_def in self.relationships().items():

            if self.meta('extends'):
                base_schema = self.cls()(self.meta('extends.schema_name'))
                if key in base_schema.column_keys():
                    continue

            relationship = self.process_relation_model(key, relationship_def, Model)
            setattr(Model, key, relationship)

        # process column properties
        for key, column_property_def in self.columns().items():
            if column_property_def.get('column_property') is None:
                continue
            print(key)

            setattr(Model, key, self.process_column_property_model(key, column_property_def, Model))
            
        return Model

    def cruved_ownership(self, id_role, id_organism):

        return column_property(
            select(
                [
                    case(
                        [
                            (TDatasets.id_digitizer == id_role, 1),
                            (TDatasets.cor_dataset_actor.any(id_role=id_role), 1),
                            (TDatasets.cor_dataset_actor.any(id_organism=id_organism), 2),
                        ],
                        else_=3
                    )
                ]
            )
            .where(self.Model().id_dataset == TDatasets.id_dataset)
        )
