'''
    SchemaMethods : serializers

    Utilisation de marshmallow
'''

from geoalchemy2.shape import to_shape, from_shape
from geojson import Feature
from marshmallow import pre_load, post_load, fields, ValidationError
from marshmallow_sqlalchemy.convert import ModelConverter
from shapely.geometry import asShape
from sqlalchemy.orm import ColumnProperty

from utils_flask_sqla_geo.utilsgeometry import remove_third_dimension
from geonature.utils.env import MA

from .errors import SchemaProcessedPropertyError
from geoalchemy2.types import Geometry as GeometryType

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

    def marshmallow_schema_name(self):
        '''
        '''

        return self.meta('marshmallow_schema_name', 'MA{}'.format(self.schema_name('pascal_case')))

    def marshmallow_meta_name(self):
        return 'Meta{}'.format(self.marshmallow_schema_name())

    def clear_cache_marshmallow(self):
        if cache_marshmallow.get(self.schema_name()):
            del cache_marshmallow[self.schema_name()]

    def process_column_marshmallow(self, column_def):
        field_type = column_def.get('type')

        kwargs = {
            'allow_none': True
        }

        if column_def.get('primary_key'):
            return fields.Integer(**kwargs)
            # return MA.auto_field(**kwargs)

        if field_type == 'integer':
            return fields.Integer(**kwargs)

        if field_type == 'number':
            return fields.Number(**kwargs)

        if field_type == 'string':
            return fields.String(**kwargs)

        if field_type == 'date':
            return fields.Date(format="%Y-%m-%d", **kwargs)

        if field_type == 'uuid':
            return fields.UUID(**kwargs)

        if field_type == 'boolean':
            return fields.Boolean(**kwargs)

        if field_type == 'geometry':
            return GeojsonSerializationField(**kwargs)

        raise SchemaProcessedPropertyError('type {} non traité'.format(column_def['type']))

    def opposite_relation_def(self, relation_def):
        return {
            'relation_type': (
                'n-1' if relation_def['relation_type'] == '1-n'
                else '1-n' if relation_def['relation_type'] == 'n-1'
                else 'n-n'
            ),
            'schema_name': self.schema_name(),
            'local_key': relation_def.get('foreign_key'),
            'foreign_key': relation_def.get('local_key'),
        }

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

        relation = self.cls()(relation_def['schema_name'])
        exclude = relation.excluded_realions(self.opposite_relation_def(relation_def))
        relation_serializer = None

        relation_serializer = fields.Nested(relation.marshmallow_schema_name(), exclude=exclude, dump_default=None)

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

        if MarshmallowSchema := cache_marshmallow.get(self.schema_name()):
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
                    data.pop(key, None)

            # pour les nested non required
            for relation_key, relation_def in self.relationships().items():
                # TODO test required
                if (
                    relation_key in data
                    and data[relation_key] is None
                    and not self.is_required(key)
                ):
                    data.pop(relation_key)

            return data

        marshmallow_schema_dict = {
            'Meta': Meta,
            'pre_load_make_object': pre_load_make_object,
            'load_fk': True
        }

        # cache_marshmallow_schema_dict[self.schema_name()] = marshmallow_schema_dict

        for key, column_def in self.columns().items():
            marshmallow_schema_dict[key] = self.process_column_marshmallow(column_def)

        # store in cache before realtion(avoid circular dependancies)
        for key, relation_def in self.relationships().items():
            marshmallow_schema_dict[key] = self.process_relation_marshmallow(relation_def)

            if relation_def.get('column_property', {}).get('type') == 'nb':
                marshmallow_schema_dict['nb_{}'.format(key)] = fields.Integer()

        if self.meta('check_cruved'):
            marshmallow_schema_dict['cruved_ownership'] = fields.Integer(dumps_only=True)

        MarshmallowSchema = type(
            self.marshmallow_schema_name(),
            (MA.SQLAlchemyAutoSchema,),
            marshmallow_schema_dict
        )

        cache_marshmallow[self.schema_name()] = MarshmallowSchema

        # load dependancies
        for dep in self.dependencies():
            sm = self.cls()(dep)
            sm.MarshmallowSchema()

        return MarshmallowSchema

    def serialize(self, m, fields=None, as_geojson=False, geometry_field_name=None):
        '''
            serialize using marshmallow

            fields = None => on renvoie tous les champs
        '''

        kwargs = {'only': fields} if fields else {}

        if as_geojson:
            geometry_field_name = geometry_field_name or self.meta('geometry_field_name')
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

            geometry_field_name = geometry_field_name or self.meta('geometry_field_name')
            if fields and geometry_field_name not in fields:
                fields.append(geometry_field_name)

        marshmallowSchema = self.MarshmallowSchema()(**kwargs)

        data_list = marshmallowSchema.dump(m_list, many=True)

        key_debug = 'nb_passages_faune'
        if hasattr(marshmallowSchema, key_debug):
            for m in m_list:
                print(getattr(m, key_debug))
        else:
            print('no {} {}'.format(self.schema_name(), key_debug))

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
        geometry_field_name = geometry_field_name or self.meta('geometry_field_name')
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
        try:
            ms.load(data, instance=m)
        except Exception as e:
            return e
