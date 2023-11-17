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

        return self.attr("meta.model_name", f"T{self.schema_code('pascal_case')}")

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
                local_key = relationship_def.get("local_key") or self.Model().pk_field_name()
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
                kwargs["primaryjoin"] = getattr(
                    self.Model(), self.Model().pk_field_name()
                ) == getattr(
                    CorTable.c, relationship_def.get("local_key", self.Model().pk_field_name())
                )
                kwargs["secondaryjoin"] = getattr(
                    relation.Model(), relation.Model().pk_field_name()
                ) == getattr(
                    CorTable.c,
                    relationship_def.get("foreign_key", self.Model().pk_field_name()),
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
        local_key = self.Model().pk_field_name()
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
        """ """
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

        raise Exception(f"Pas de modele trouvé !!! pour {self.schema_code()}")
