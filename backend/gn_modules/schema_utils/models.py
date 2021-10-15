'''
    SchemaMethods : sqlalchemy models processing
'''

from geoalchemy2 import Geometry
from sqlalchemy.orm import column_property
from sqlalchemy.orm import object_session
from sqlalchemy import select, func, cast, text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from geonature.utils.env import DB

from .errors import SchemaProcessedPropertyError

# store the sqla models
cache_model = {}

class SchemaModel():
    '''
        sqlalchemy models processing
    '''

    def model_name(self):
        '''
            returns model_name
            can be
              - defined in self._schema['$meta']['model_name']
              - or retrieved from group_name and object_name 'T{full_name('pascal_case')}'
        '''

        return self._schema['$meta'].get('model_name', 'T{}'.format(self.full_name('pascal_case')))

    def clear_cache_model(self):
        if cache_model.get(self.full_name()):
            del cache_model[self.full_name()]

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
        if Model:= cache_model.get(self.full_name()):
            return Model

        # dict_model used with type() to list properties and methods for class creation
        dict_model = {
            '__tablename__': self.sql_table_name(),
            '__table_args__': {
                'schema': self.sql_schema_name(),
                'extend_existing': True # TODO remove and storage for class
            }
        }

        # process properties
        for key, value in self.properties(processed_properties_only=True).items():

            # get field_options
            field_args = []
            field_kwargs = {}
            field_type = value['type']

            # primary key
            if value.get('primary_key'):
                field_kwargs['primary_key'] = True
                pk_key = key
            # foreign_key
            if value.get('foreign_key'):
                relation_reference = value['foreign_key']
                sm_relation = self.__class__().load_from_reference(relation_reference)
                foreign_key = '{}.{}'.format(sm_relation.sql_schema_dot_table(), sm_relation.pk_field_name())
                field_args.append(DB.ForeignKey(foreign_key))

            # process type
            if field_type == 'integer':
                dict_model[key] = DB.Column(DB.Integer, *field_args, **field_kwargs)
            elif field_type == 'string':
                dict_model[key] = DB.Column(DB.Unicode, *field_args, **field_kwargs)
            elif field_type == 'date':
                dict_model[key] = DB.Column(DB.DateTime, *field_args, **field_kwargs)
            elif field_type == 'uuid':
                print('a', key, 'a')
                field_kwargs['as_uuid']= True
                dict_model[key] = DB.Column(UUID, *field_args, **field_kwargs)
            elif field_type == 'geom':
                dict_model[key] = DB.Column(Geometry(value['geom_type'], value['srid']), *field_args, **field_kwargs)
            else:
                raise(
                    SchemaProcessedPropertyError(
                    'Property type {} in processed_properties but not managed yet for Models processing'
                    .format(field_type)
                )
            )

        # process relations

        for key, value in self.relationships().items():
            # get ref from foreign_key
            foreign_key = value['foreign_key']
            relation_reference = self.properties()[foreign_key]['foreign_key']
            sm_relation = self.__class__().load_from_reference(relation_reference)

            dict_model[key] = DB.relationship(sm_relation.Model())

        # create class for Model
        Model = type(self.model_name(), (DB.Model,), dict_model)

        # for key, value in self.properties(processed_properties_only=True).items():
        #     if field_type == 'geom':

        #         def geom_as_geojson(self_model):
        #             return object_session(self_model).\
        #             scalar(
        #                 select([
        #                     func.st_asgeojson(getattr(Model, key))
        #                 ]).where(
        #                         getattr(Model, self.pk_field_name())
        #                         ==
        #                         getattr(self_model, self.pk_field_name())
        #                 )
        #             )

        #         setattr(Model, key + '_as_geojson', property(geom_as_geojson))

        # store in cache
        cache_model[self.full_name()] = Model

        return Model