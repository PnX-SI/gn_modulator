'''
    SchemaMethods : serializers

    Utilisation de marshmallow
'''

import json
from marshmallow import pre_load, post_load, pre_dump, fields, ValidationError
from sqlalchemy.orm import ColumnProperty

from shapely.geometry import asShape
from geoalchemy2.shape import to_shape, from_shape
from geoalchemy2.types import Geometry as GeometryType
from geojson import Feature, FeatureCollection

from .queries import custom_getattr 


from geonature.utils.env import (MA, DB)

from .errors import SchemaProcessedPropertyError
from sqlalchemy import func
# store the marshmallow schema
cache_marshmallow = {}

class GeojsonSerializationField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return value
        else:
            if type(value).__name__ == "WKBElement":
                # return json.loads(getattr(obj, attr+ '_as_geojson'))
                feature = Feature(geometry=to_shape(value))
                return feature.geometry
            else:
                return None

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            shape = asShape(value)
            two_dimension_geom = remove_third_dimension(shape)
            return from_shape(two_dimension_geom, srid=4326)
        except ValueError as error:
            raise ValidationError("Geometry error") from error


class SchemaSerializers:
    '''
        schema model serializer class

        TODO
    '''

    def marshmallow_object_name(self):
        '''
            returns marshmallow_object_name
            can be
            - defined in self._schema['$meta']['marshmallow_object_name']
            - or retrieved from group_name and object_name 'T{full_name('pascal_case')}'
        '''

        return self._schema['$meta'].get('marshmallow_object_name', 'MA{}'.format(self.full_name('pascal_case')))

    def marshmallow_meta_name(self):
        return 'Meta{}'.format(self.marshmallow_object_name())

    def clear_cache_marshmallow(self):
        if cache_marshmallow.get(self.full_name()):
            del cache_marshmallow[self.full_name()]


    def excluded_fields(self):
        '''
            pour exclure la geometrie à traiter plus tard
        '''
        excluded_fields = []
        # boucle sur les champs de Models
        schema_properties_keys = self.properties(processed_properties_only=True).keys()
        for prop in self.Model().__mapper__.column_attrs:
            if isinstance(prop, ColumnProperty):  # and len(prop.columns) == 1:
                # -1 : si on est dans le cas d'un heritage on recupere le dernier element de prop
                # qui correspond à la derniere redefinition de cette colonne
                db_col = prop.columns[-1]
                # HACK
                #  -> Récupération du nom de l'attribut sans la classe
                name = str(prop).split('.', 1)[1]
                if db_col.type.__class__.__name__ == 'Geometry' and (name not in schema_properties_keys):
                    excluded_fields.append(name)

        return excluded_fields


    def MarshmallowShema(self):
        '''
        '''

        if MarshmallowShema := cache_marshmallow.get(self.full_name()):
            return MarshmallowShema

        print('MarshmallowShema create  ', self.full_name())

        marshmallow_meta_dict = {
            'model': self.Model(),
            'load_instance': True,
            'exclude': self.excluded_fields()
        }

        Meta = type(self.marshmallow_meta_name(), (), marshmallow_meta_dict)

        '''
            remove pk_key from data when pk_key is None
        '''
        @pre_load
        def pre_load_make_object(self_marshmallow, data, **kwargs):
            for key in self.pk_field_names():
                if key in data and data[key] is None:
                    data.pop(key, None)
            return data

        marshmallow_schema_dict = {
            'Meta': Meta,
            'pre_load_make_object': pre_load_make_object
        }

        for key, value in self.properties(processed_properties_only=True).items():
            if value.get('primary_key'):
                marshmallow_schema_dict[key] = MA.auto_field()
            elif value['type'] == 'integer':
                marshmallow_schema_dict[key] = fields.Integer()
            elif value['type'] == 'number':
                marshmallow_schema_dict[key] = fields.Number()
            elif value['type'] == 'text':
                marshmallow_schema_dict[key] = fields.String()
            elif value['type'] == 'date':
                marshmallow_schema_dict[key] = fields.Date(format="%Y-%m-%d")
            elif value['type'] == 'geom':
                marshmallow_schema_dict[key] = GeojsonSerializationField()

            else:
                 raise SchemaProcessedPropertyError('type {} non traité'.format(value['type']))

        for key, value in self.relationships().items():
            foreign_key = value['foreign_key']
            relation_reference = self.properties()[foreign_key]['foreign_key']
            sm_relation = self.__class__().load_from_reference(relation_reference)

            marshmallow_schema_dict[key] = MA.Nested(sm_relation.MarshmallowShema())

        # create Class for MarshmallowShema
        MarshmallowShema = type(self.marshmallow_object_name(), (MA.SQLAlchemyAutoSchema,), marshmallow_schema_dict)

        # store in cache
        cache_marshmallow[self.full_name()] = MarshmallowShema

        return MarshmallowShema

    def serialize(self, m, fields = None):
        '''
            serialize using marshmallow

            fields = None => on renvoie tous les champs
        '''

        kwargs = { 'only': fields } if fields else {}

        return ( self.MarshmallowShema()
            (**kwargs)
            .dump(m)
        )


    def serialize2(self, m, fields = None):
        '''
            serialize alamano

            fields = None => on renvoie tous les champs
        '''

        d = {

        }

        for f in fields:
            d[f], _ = custom_getattr(m, f)

        return d


    def serialize_list(self, m_list, fields = None):
        '''
            serialize using marshmallow

            fields = None => on renvoie tous les champs
        '''

        kwargs = { 'only': fields } if fields else {}

        marshmallowSchema = self.MarshmallowShema()(**kwargs)


        return marshmallowSchema.dump(m_list, many=True)
        # return [marshmallowSchema.dump(m) for m in m_list]


    def unserialize(self, m, data):
        '''
            unserialize using marshmallow
        '''
        MS = self.MarshmallowShema()
        ms = MS()
        return ms.load(data, instance=m)
