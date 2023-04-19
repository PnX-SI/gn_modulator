"""
    SchemaMethods : sqlalchemy existing_Models processing
"""

import uuid
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geonature.utils.env import db
from ..errors import SchemaProcessedPropertyError
from gn_modulator.utils.cache import get_global_cache, set_global_cache
from utils_flask_sqla.serializers import serializable

# store the sqla Models


class SchemaModelBase:
    """
    sqlalchemy Models processing
    """

    def model_name(self):
        """ """

        return self.attr("meta.model_name", "T{}".format(self.schema_code("pascal_case")))

    def get_db_type(self, column):
        field_type = column.get("type")

        if field_type == "integer":
            return db.Integer
        if field_type == "json":
            return JSONB
        if field_type == "boolean":
            return db.Boolean
        if field_type == "number":
            return db.Float
        if field_type == "string":
            return db.Unicode
        if field_type == "uuid":
            return UUID(as_uuid=True)
        if field_type == "date":
            return db.Date
        if field_type == "datetime":
            return db.DateTime
        if field_type == "geometry":
            return Geometry(column["geometry_type"], column["srid"])

        raise (SchemaProcessedPropertyError("db_type is None for prop {}".format(column)))

    def process_existing_column_model(self, key, column_def, column_model):
        pass

    def process_column_model(self, key, column_def):
        """ """
        # get field_options
        field_args = []
        field_kwargs = {}
        db_type = None

        # primary key
        if column_def.get("primary_key"):
            field_kwargs["primary_key"] = True

        # foreign_key
        if column_def.get("foreign_key"):
            relation = self.cls(column_def["schema_code"])
            foreign_key = "{}.{}".format(relation.sql_schema_dot_table(), relation.pk_field_name())
            if self.is_required(key):
                field_args.append(
                    db.ForeignKey(foreign_key, ondelete="CASCADE", onupdate="CASCADE")
                )
            else:
                field_args.append(db.ForeignKey(foreign_key))

        # process type
        db_type = self.get_db_type(column_def)

        # default
        if column_def.get("default"):
            field_kwargs["default"] = self.process_default_model(column_def)

        return db.Column(db_type, *field_args, **field_kwargs)

    def process_default_model(self, column_def):
        if column_def["type"] == "uuid":
            return uuid.uuid4

    def process_relation_model(self, key, relationship_def, Model):
        relation = self.cls(relationship_def["schema_code"])

        if not relation.Model():
            return

        kwargs = {}
        # if relationship_def.get('backref'):
        #     kwargs['backref'] = relationship_def.get('backref')

        if relationship_def.get("relation_type") == "1-1":
            kwargs["uselist"] = False

        if relationship_def.get("relation_type") == "1-n":
            # test si obligatoire
            rel = self.cls(relationship_def["schema_code"])

            if relationship_def.get("local_key"):
                local_key = relationship_def.get("local_key") or self.pk_field_name()
                foreign_key = relationship_def.get("foreign_key")
                kwargs["primaryjoin"] = getattr(self.Model(), local_key) == getattr(
                    relation.Model(), foreign_key
                )
                kwargs["foreign_keys"] = [getattr(relation.Model(), foreign_key)]

            if rel.is_required(relationship_def["foreign_key"]):
                kwargs["cascade"] = "all, delete, delete-orphan"
            # if foreign_column.requi

        if relationship_def.get("relation_type") == "n-1":
            kwargs["foreign_keys"] = getattr(Model, relationship_def["local_key"])

            # patch si la cle n'est pas definie
            column_def = self.column(relationship_def["local_key"])
            relation = self.cls(column_def["schema_code"])

            kwargs["primaryjoin"] = getattr(
                self.Model(), relationship_def["local_key"]
            ) == getattr(relation.Model(), relation.pk_field_name())

        if relationship_def.get("relation_type") == "n-n":
            CorTable = self.CorTable(relationship_def)
            kwargs["secondary"] = CorTable
            if (
                # True or
                relationship_def.get("local_key")
                and relationship_def.get("foreign_key")
            ):
                kwargs["primaryjoin"] = getattr(self.Model(), self.pk_field_name()) == getattr(
                    CorTable.c, relationship_def.get("local_key", self.pk_field_name())
                )
                kwargs["secondaryjoin"] = getattr(
                    relation.Model(), relation.pk_field_name()
                ) == getattr(
                    CorTable.c,
                    relationship_def.get("foreign_key", self.pk_field_name()),
                )

        relationship = db.relationship(relation.Model(), **kwargs)
        return relationship

    def CorTable(self, relation_def):
        # cas cor_schema_code
        cor_schema_code = relation_def.get("cor_schema_code")
        if cor_schema_code:
            sm_cor = self.cls(cor_schema_code)
            Model = sm_cor.Model()
            CorTable = Model.__table__
            return CorTable

        schema_dot_table = relation_def.get("schema_dot_table")
        cor_schema_code = schema_dot_table.split(".")[0]
        cor_table_name = schema_dot_table.split(".")[1]

        CorTable = get_global_cache(["cor_table", schema_dot_table])

        if CorTable is not None:
            return CorTable

        CorTable = self.get_cache_existing_tables(schema_dot_table)

        if CorTable is not None:
            return CorTable

        relation = self.cls(relation_def["schema_code"])
        local_key = self.pk_field_name()
        foreign_key = relation.pk_field_name()
        CorTable = db.Table(
            cor_table_name,
            db.metadata,
            db.Column(
                local_key,
                db.ForeignKey(f"{self.sql_schema_dot_table()}.{local_key}"),
                primary_key=True,
            ),
            db.Column(
                foreign_key,
                db.ForeignKey(f"{relation.sql_schema_dot_table()}.{foreign_key}"),
                primary_key=True,
            ),
            schema=cor_schema_code,
        )

        set_global_cache(["cor_table", schema_dot_table], CorTable)

        return CorTable

    def Model(self):
        """
        create and returns schema Model : a class created with type(name, (bases,), dict_model) function
        - name : self.model_name()
        - base :  db.Model
        - dict_model : contains properties and methods

        TODO store in global variable and create only if missing
        - avoid to create the model twice
        """
        if not self.sql_table_exists():
            return None

        # get Model from cache
        Model = get_global_cache(["schema", self.schema_code(), "model"])
        if Model:
            return Model

        # get Model from existing
        Model = self.get_existing_model()
        if Model:
            return Model

        # dict_model used with type() to list properties and methods for class creation
        dict_model = {
            "__tablename__": self.sql_table_name(),
            "__table_args__": {
                "schema": self.sql_schema_name(),
            },
        }

        ModelBaseClass = db.Model

        # process properties
        for key, column_def in self.columns().items():
            if column_def.get("column_property") is not None:
                continue

            dict_model[key] = self.process_column_model(key, column_def)

        Model = type(self.model_name(), (ModelBaseClass,), dict_model)

        # patch cruved
        Model.ownership = 0

        # store in cache before relations (avoid circular dependencies)
        set_global_cache(["schema", self.schema_code(), "model"], Model)

        # process relations

        for key, relationship_def in self.relationships().items():
            relationship = self.process_relation_model(key, relationship_def, Model)
            setattr(Model, key, relationship)
        # process column properties
        for key, column_property_def in self.column_properties().items():
            setattr(
                Model,
                key,
                self.process_column_property_model(key, column_property_def, Model),
            )

        set_global_cache(["schema", self.schema_code(), "model"], serializable(Model))

        return Model

    def process_backrefs(self):
        """
        ajout des definition des relation avec backref dans le schema correspondant
        """
        for relation_key, relation_def in self.relationships().items():
            if not relation_def.get("backref"):
                continue

            opposite = self.opposite_relation_def(relation_def)
            rel = self.cls(relation_def["schema_code"])
            rel_properties = rel.attr("properties")
            if not rel_properties.get(relation_def["backref"]):
                rel_properties[relation_def["backref"]] = opposite
