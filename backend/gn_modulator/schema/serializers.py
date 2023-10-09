"""
    SchemaMethods : serializers

    Utilisation de marshmallow
"""

from geoalchemy2.shape import to_shape, from_shape
from geoalchemy2.functions import ST_Transform
from geojson import Feature
from marshmallow import pre_load, fields, ValidationError, EXCLUDE
from shapely.geometry import shape
from utils_flask_sqla_geo.utilsgeometry import remove_third_dimension
from geonature.utils.env import ma
from .errors import SchemaProcessedPropertyError
from gn_modulator.utils.cache import get_global_cache, set_global_cache
from gn_modulator import MODULE_CODE
from sqlalchemy.orm.exc import NoResultFound
from geonature.utils.env import db


class GeojsonSerializationField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return value
        else:
            if type(value).__name__ == "WKBElement":
                feature = Feature(geometry=to_shape(value))
                return feature.geometry
            else:
                return None

    # on assume ici que toutes les geometrie sont en srid local sauf indication dans value
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            shape_from_value = shape(value)
            two_dimension_geom = remove_third_dimension(shape_from_value)
            return from_shape(two_dimension_geom, srid=4326)
        except ValueError as error:
            raise ValidationError("Geometry error") from error


class SchemaSerializers:
    """
    schema model serializer class

    TODO
    """

    def marshmallow_schema_code(self):
        """ """

        return self.attr(
            "meta.marshmallow_schema_code",
            "ma{}".format(self.schema_code("pascal_case")),
        )

    def marshmallow_meta_name(self):
        return "Meta{}".format(self.marshmallow_schema_code())

    def process_column_marshmallow(self, column_key, column_def):
        field_type = column_def.get("type")

        kwargs = {"allow_none": True}

        if column_def.get("load_only"):
            kwargs["load_only"] = True

        if column_def.get("dump_only"):
            kwargs["dump_only"] = True

        if column_def.get("primary_key"):
            return fields.Integer(**kwargs)

        if field_type == "integer":
            return fields.Integer(**kwargs)

        if field_type == "number":
            return fields.Number(**kwargs)

        if field_type == "string":
            return fields.String(**kwargs)

        if field_type == "datetime":
            return fields.DateTime(**kwargs)

        if field_type == "date":
            # kwargs['format'] = column_def.get('format', "%Y-%m-%d")
            return fields.Date(**kwargs)

        if field_type == "uuid":
            return fields.UUID(**kwargs)

        if field_type == "boolean":
            return fields.Boolean(**kwargs)

        if field_type == "geometry":
            return GeojsonSerializationField(**kwargs)

        if field_type == "json":
            return fields.Raw(**kwargs)

        raise SchemaProcessedPropertyError("type {} non traité".format(column_def["type"]))

    def opposite_relation_def(self, relation_def):
        opposite = {
            "type": "relation",
            "relation_type": (
                "n-1"
                if relation_def["relation_type"] == "1-n"
                else "1-n"
                if relation_def["relation_type"] == "n-1"
                else "1-1"
                if relation_def["relation_type"] == "1-1"
                else "n-n"
            ),
            "schema_code": self.schema_code(),
            "title": self.attr("meta.label"),
        }
        if relation_def.get("foreign_key"):
            opposite["local_key"] = relation_def.get("foreign_key")
        if relation_def.get("local_key"):
            opposite["foreign_key"] = relation_def.get("local_key")
        if relation_def.get("schema_dot_table"):
            opposite["schema_dot_table"] = relation_def.get("schema_dot_table")
        if relation_def.get("cor_schema_code"):
            opposite["cor_schema_code"] = relation_def.get("cor_schema_code")
        return opposite

    def is_relation_excluded(self, relation_def_test, relation_def):
        return (
            relation_def.get("relation_type") == relation_def_test.get("relation_type")
            and relation_def.get("schema_code") == relation_def_test.get("schema_code")
            and relation_def.get("local_key") == relation_def_test.get("local_key")
            and relation_def.get("foreign_key") == relation_def_test.get("foreign_key")
        )

    def excluded_relations(self, relation_def_test):
        return [
            key
            for key, relation_def in self.relationships().items()
            if self.is_relation_excluded(relation_def_test, relation_def)
        ]

    def process_relation_marshmallow(self, relation_key, relation_def):
        # kwargs = {}
        # kwargs['exclude_relations'] = [self.opposite_relation_def(relation_def)]

        # avoid circular dependencies

        relation = self.cls(relation_def["schema_code"])
        if not relation.Model():
            return None

        exclude = relation.excluded_relations(self.opposite_relation_def(relation_def))

        relation_serializer = fields.Nested(
            relation.marshmallow_schema_code(),
            **{"exclude": exclude, "dump_default": None},
        )

        if relation_def["relation_type"] == "n-1":
            relation_serializer = relation_serializer
        if relation_def["relation_type"] in ["1-n", "n-n"]:
            relation_serializer = fields.List(relation_serializer)

        if relation_serializer is None:
            raise Exception("relation_serializer is None for {}".format(relation_def))

        return relation_serializer

    def MarshmallowSchema(self, force=False):
        """
        False permet de recréer le schema si besoin
        """

        MarshmallowSchema = get_global_cache(["schema", self.schema_code(), "marshmallow"])

        if MarshmallowSchema is not None and not force:
            return MarshmallowSchema

        if self.Model() is None:
            return None

        marshmallow_meta_dict = {
            "model": self.Model(),
            "load_instance": True,
        }

        Meta = type(self.marshmallow_meta_name(), (), marshmallow_meta_dict)

        """
            remove pk_key from data when pk_key is None
        """

        @pre_load
        def pre_load_make_object(self_marshmallow, data, **kwargs):
            for key in self.pk_field_names():
                if key in data and data[key] is None:
                    data.pop(key, None)

            # enleve les clés si non dans only
            for k in list(data.keys()):
                if self_marshmallow.only and k not in self_marshmallow.only:
                    print(self, "pop not in only", k)
                    data.pop(k)

            # # pour les champs null avec default d
            #
            # efini dans les proprietés
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
                    if property.get("relation_type") in ["n-1", "n-n"] and data[k] is None:
                        data.pop(k)
                # rem ove extra items
                else:
                    data.pop(k)

            # remove array when null
            return data

        marshmallow_schema_dict = {
            "Meta": Meta,
            "pre_load_make_object": pre_load_make_object,
            "load_fk": True,
        }

        for column_key, column_def in self.columns().items():
            marshmallow_schema_dict[column_key] = self.process_column_marshmallow(
                column_key, column_def
            )

        for column_key, column_def in self.column_properties().items():
            if column_def["type"] == "relation":
                continue
            marshmallow_schema_dict[column_key] = self.process_column_marshmallow(
                column_key, column_def
            )

        # if self.attr('meta.check_cruved'):
        marshmallow_schema_dict["scope"] = fields.Integer(metadata={"dumps_only": True})
        marshmallow_schema_dict["row_number"] = fields.Integer(metadata={"dumps_only": True})
        # else:
        # marshmallow_schema_dict['scope'] = 0

        # store in cache before relation (avoid circular dependencies)

        for relation_key, relation_def in self.relationships().items():
            relation_marshmallow = self.process_relation_marshmallow(relation_key, relation_def)

            if not relation_marshmallow:
                continue

            marshmallow_schema_dict[relation_key] = relation_marshmallow

        MarshmallowSchema = type(
            self.marshmallow_schema_code(),
            (ma.SQLAlchemyAutoSchema,),
            marshmallow_schema_dict,
        )

        set_global_cache(["schema", self.schema_code(), "marshmallow"], MarshmallowSchema)

        # load dependencies
        for dep in self.dependencies():
            sm = self.cls(dep)
            sm.MarshmallowSchema()

        return MarshmallowSchema

    def serialize(self, m, fields=None, as_geojson=False, geometry_field_name=None):
        """
        serialize using marshmallow

        fields = None => on renvoie tous les champs
        """

        if not fields:
            fields = [self.pk_field_name()]

        # quand une relation est demandée
        # on veut éviter de sortir toute la base dans la foulée
        # par défaut on demande pk et label
        fields_to_remove = []
        fields_to_add = []

        for field in fields:
            property = self.property(field)
            if property is None or property["type"] != "relation":
                continue
            sm_rel = self.cls(property["schema_code"])

            fields_to_remove.append(field)
            default_fields = sm_rel.attr("meta.default_fields")
            if default_fields:
                for rel_field in default_fields:
                    fields_to_add.append(f"{field}.{rel_field}")
            else:
                fields_to_add.append(f"{field}.{sm_rel.pk_field_name()}")
                fields_to_add.append(f"{field}.{sm_rel.label_field_name()}")

        for f in fields_to_remove:
            fields.remove(f)

        fields += fields_to_add

        kwargs = {"only": fields} if fields else {}

        if as_geojson:
            geometry_field_name = geometry_field_name or self.attr("meta.geometry_field_name")
            if fields and geometry_field_name not in fields:
                fields.append(geometry_field_name)

        data = self.MarshmallowSchema()(**kwargs).dump(m[0] if isinstance(m, tuple) else m)

        # pour gérer les champs supplémentaire (scope, row_number, etc....)
        if isinstance(m, tuple):
            keys = list(m.keys())
            if len(keys) > 1:
                keys = keys[1:]

                for key in keys:
                    data[key] = getattr(m, key)

        if as_geojson:
            return self.as_geojson(data, geometry_field_name)
        else:
            return data

    def get_row_as_dict(
        self,
        value,
        field_name=None,
        module_code=MODULE_CODE,
        cruved_type="R",
        fields=None,
        query_type="all",
        as_geojson=False,
        geometry_field_name=None,
    ):
        """
        enchaine en une seule commande get_row et serialize
        si la ligne n'est pas trouvée, on renvoie None
        """
        try:
            m = self.get_row(
                value,
                field_name=field_name,
                module_code=module_code,
                cruved_type=cruved_type,
                params={"fields": fields},
                query_type=query_type,
            ).one()

        except NoResultFound:
            return None

        return self.serialize(
            m,
            fields=fields,
            as_geojson=as_geojson,
            geometry_field_name=geometry_field_name,
        )

    def serialize_list(
        self,
        m_list,
        fields=None,
        as_geojson=False,
        geometry_field_name=False,
        flat_keys=False,
    ):
        """
        serialize using marshmallow

        fields = None => on renvoie tous les champs
        """

        kwargs = {"only": fields} if fields else {}

        if as_geojson:
            geometry_field_name = geometry_field_name or self.attr("meta.geometry_field_name")
            if fields and geometry_field_name not in fields:
                fields.append(geometry_field_name)

        marshmallowSchema = self.MarshmallowSchema()(**kwargs)
        data_list = marshmallowSchema.dump(
            map(lambda x: x[0] if isinstance(x, tuple) else x, m_list), many=True
        )

        # pour gérer les champs supplémentaire (scope, row_number, etc....)
        if len(data_list) and isinstance(m_list[0], tuple):
            keys = list(m_list[0].keys())
            if len(keys) > 1:
                keys = keys[1:]

                for index, res in enumerate(m_list):
                    for key in keys:
                        data_list[index][key] = getattr(res, key)

        if as_geojson:
            features = []
            for data in data_list:
                features.append(self.as_geojson(data, geometry_field_name))
            return {"type": "FeatureCollection", "features": features}

        else:
            if flat_keys:
                return [{key: self.process_csv_data(key, d) for key in fields} for d in data_list]
            return data_list

    def as_geojson(self, data, geometry_field_name=None):
        geometry_field_name = geometry_field_name or self.attr("meta.geometry_field_name")
        geometry = data.pop(geometry_field_name)
        return {"type": "Feature", "geometry": geometry, "properties": data}

    def unserialize(self, m, data, authorized_write_fields=None):
        """
        unserialize using marshmallow
        """
        kwargs = {}
        if authorized_write_fields:
            kwargs = {"only": authorized_write_fields, "unknown": EXCLUDE}
        MS = self.MarshmallowSchema()

        ms = MS(**kwargs)

        ms.load(data, instance=m)

    @classmethod
    def reinit_marshmallow_schemas(cls):
        """
        methode pour reinitialiser les schemas
        par exemple pour un install après une migration
        et pour l'installation de données complémentaire exemple
        on a besoin de refaire les schema qui n'ont pas pu être fait correctement car des tables n'existaient pas
        (pas de model pour les relations -> schema non operationel pour ces relation)
        """
        for schema_code in cls.schema_codes():
            set_global_cache(["schema", schema_code, "marshmallow"], None)

        for schema_code in cls.schema_codes():
            sm = cls(schema_code)

        for schema_code in cls.schema_codes():
            sm = cls(schema_code)
            sm.Model()

        for schema_code in cls.schema_codes():
            sm = cls(schema_code)
            sm.MarshmallowSchema()
