'''
    SchemaMethods : serializers

    Utilisation de marshmallow
'''

import copy
from geoalchemy2.shape import to_shape, from_shape
from geoalchemy2 import functions
from geojson import Feature
from marshmallow import pre_load, post_load, fields, ValidationError
from shapely.geometry import shape
from sqlalchemy.orm import ColumnProperty

from utils_flask_sqla_geo.utilsgeometry import remove_third_dimension
from geonature.utils.env import ma

from .errors import SchemaProcessedPropertyError, SchemaSerializerModelIsNoneError
from geoalchemy2.types import Geometry as GeometryType

# store the marshmallow schema

import json
class GeojsonSerializationField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return value
        else:
            if type(value).__name__ == "WKBElement":
                feature = Feature(
                    geometry=to_shape(value)
                )
                return feature.geometry
            else:
                return None

    # on assume ici que toutes les geometrie sont en srid local sauf indication dans value
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            shape_from_value = shape(value)
            two_dimension_geom = remove_third_dimension(shape_from_value)
            return from_shape(
                two_dimension_geom,
                srid=4326
            )
        except ValueError as error:
            raise ValidationError("Geometry error") from error


class SchemaSerializers:
    '''
        schema model serializer class

        TODO
    '''

    def marshmallow_schema_name(self):
        '''
        '''

        return self.attr('meta.marshmallow_schema_name', 'ma{}'.format(self.schema_name('pascal_case')))

    def marshmallow_meta_name(self):
        return 'Meta{}'.format(self.marshmallow_schema_name())


    def process_column_marshmallow(self, column_def):
        field_type = column_def.get('type')
        kwargs = {
            'allow_none': True
        }

        if column_def.get('primary_key'):
            return fields.Integer(**kwargs)

        if field_type == 'integer':
            return fields.Integer(**kwargs)

        if field_type == 'number':
            return fields.Number(**kwargs)

        if field_type == 'string':
            return fields.String(**kwargs)

        if field_type == 'date':
            # kwargs['format'] = column_def.get('format', "%Y-%m-%d")
            return fields.Date(**kwargs)

        if field_type == 'uuid':
            return fields.UUID(**kwargs)

        if field_type == 'boolean':
            return fields.Boolean(**kwargs)

        if field_type == 'geometry':
            return GeojsonSerializationField(**kwargs)

        if field_type == 'json':
            return fields.Raw(**kwargs)


        print(column_def)
        aa
        raise SchemaProcessedPropertyError('type {} non traité'.format(column_def['type']))

    def opposite_relation_def(self, relation_def):
        opposite = {
            'type': 'relation',
            'relation_type': (
                'n-1' if relation_def['relation_type'] == '1-n'
                else '1-n' if relation_def['relation_type'] == 'n-1'
                else '1-1' if relation_def['relation_type'] == '1-1'
                else 'n-n'
            ),
            'schema_name': self.schema_name(),
            'title': self.attr('meta.label')
        }
        if relation_def.get('foreign_key'):
            opposite['local_key'] = relation_def.get('foreign_key')
        if relation_def.get('local_key'):
            opposite['foreign_key'] = relation_def.get('local_key')
        if relation_def.get('schema_dot_table'):
            opposite['schema_dot_table'] = relation_def.get('schema_dot_table')

        return opposite

    def is_relation_excluded(self, relation_def_test, relation_def):
        return (
            relation_def.get('relation_type') == relation_def_test.get('relation_type')
            and relation_def.get('schema_name') == relation_def_test.get('schema_name')
            and relation_def.get('local_key') == relation_def_test.get('local_key')
            and relation_def.get('foreign_key') == relation_def_test.get('foreign_key')
        )

    def excluded_realions(self, relation_def_test):
        return [
            key
            for key, relation_def in self.relationships().items()
            if self.is_relation_excluded(relation_def_test, relation_def)
        ]

    def process_relation_marshmallow(self, relation_def):
        # kwargs = {}
        # kwargs['exclude_relations'] = [self.opposite_relation_def(relation_def)]

        # avoid circular dependencies

        relation = self.cls(relation_def['schema_name'])
        if not relation.Model():
            return None
        exclude = relation.excluded_realions(self.opposite_relation_def(relation_def))
        relation_serializer = None

        relation_serializer = fields.Nested(relation.marshmallow_schema_name(), **{"exclude":exclude, "dump_default": None})

        if relation_def['relation_type'] == 'n-1':
            relation_serializer = relation_serializer
        if relation_def['relation_type'] in ['1-n', 'n-n']:
            relation_serializer = fields.List(relation_serializer)

        if relation_serializer is None:
            raise Exception('relation_serializer is None for {}'.format(relation_def))

        return relation_serializer

    def MarshmallowSchema(self):
        '''
        '''

        if MarshmallowSchema := self.cls.get_schema_cache(self.schema_name(), 'marshmallow'):
            return MarshmallowSchema

        marshmallow_meta_dict = {
            'model': self.Model(),
            'load_instance': True,
        }

        Meta = type(self.marshmallow_meta_name(), (), marshmallow_meta_dict)

        '''
            remove pk_key from data when pk_key is None
        '''

        @pre_load
        def pre_load_make_object(self_marshmallow, data, **kwargs):

            for key in self.pk_field_names():
                if key in data and data[key] is None:
                    print('marsh remove pk null', key)
                    data.pop(key, None)

            # # pour les champs null avec default defini dans les proprietés
            # for key, column_def in self.columns().items():
            #     if key in data and data[key] is None and column_def.get('default'):
            #         data.pop(key, None)

            # pour les nested non required
            for relation_key, relation_def in self.relationships().items():
                # TODO test required
                if (
                    relation_key in data
                    and data[relation_key] is None
                    and not self.is_required(key)
                ):
                    data.pop(relation_key)

            # clean data
            for k in [k for k in data.keys()]:
                if self.has_property(k):
                    property = self.property(k)
                    # test if array
                    if property.get('relation_type') in ['n-1', 'n-n'] and data[k] is None:
                        data.pop(k)
                # rem ove extra items
                else:
                    data.pop(k)

            # remove array when null
            return data

        marshmallow_schema_dict = {
            'Meta': Meta,
            'pre_load_make_object': pre_load_make_object,
            'load_fk': True
        }

        for key, column_def in self.columns().items():
            marshmallow_schema_dict[key] = self.process_column_marshmallow(column_def)

        for key, column_def in self.column_properties().items():
            if column_def['type'] == 'relation':
                continue
            marshmallow_schema_dict[key] = self.process_column_marshmallow(column_def)

        # if self.attr('meta.check_cruved'):
        marshmallow_schema_dict['cruved_ownership'] = fields.Integer(metadata={'dumps_only': True})
        # else:
            # marshmallow_schema_dict['cruved_ownership'] = 0


        # store in cache before relation (avoid circular dependancies)
        for key, relation_def in self.relationships().items():
            relation_marshmallow = self.process_relation_marshmallow(relation_def)
            if not relation_marshmallow:
                return None


            marshmallow_schema_dict[key] = relation_marshmallow


        MarshmallowSchema = type(
            self.marshmallow_schema_name(),
            (ma.SQLAlchemyAutoSchema,),
            marshmallow_schema_dict
        )

        self.cls.set_schema_cache(self.schema_name(), 'marshmallow', MarshmallowSchema)

        # load dependancies
        for dep in self.dependencies():
            sm = self.cls(dep)
            sm.MarshmallowSchema()

        return MarshmallowSchema

    def serialize(self, m, fields=None, as_geojson=False, geometry_field_name=None):
        '''
            serialize using marshmallow

            fields = None => on renvoie tous les champs
        '''

        kwargs = {'only': fields} if fields else {}

        if as_geojson:
            geometry_field_name = geometry_field_name or self.attr('meta.geometry_field_name')
            if fields and geometry_field_name not in fields:
                fields.append(geometry_field_name)

        data = (
            self.MarshmallowSchema()
            (**kwargs)
            .dump(m)
        )

        if as_geojson:
            return self.as_geojson(data, geometry_field_name)
        else:
            return data

    def serialize_list(self, m_list, fields=None, as_geojson=False, geometry_field_name=False):
        '''
            serialize using marshmallow

            fields = None => on renvoie tous les champs
        '''

        kwargs = {'only': fields} if fields else {}

        if as_geojson:

            geometry_field_name = geometry_field_name or self.attr('meta.geometry_field_name')
            if fields and geometry_field_name not in fields:
                fields.append(geometry_field_name)

        marshmallowSchema = self.MarshmallowSchema()(**kwargs)
        data_list = marshmallowSchema.dump(m_list, many=True)

        if as_geojson:

            features = []
            for data in data_list:
                features.append(self.as_geojson(data, geometry_field_name))
            return {
                "type": "FeatureCollection",
                "features": features
            }

        else:
            return data_list

    def as_geojson(self, data, geometry_field_name=None):
        geometry_field_name = geometry_field_name or self.attr('meta.geometry_field_name')
        geometry = data.pop(geometry_field_name)
        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": data
        }

    def unserialize(self, m, data):
        '''
            unserialize using marshmallow
        '''
        MS = self.MarshmallowSchema()
        ms = MS()
        ms.load(data, instance=m)
