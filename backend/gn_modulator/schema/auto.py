"""
    AutoSchemas
"""

from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from geonature.utils.env import db
from .errors import SchemaAutoError
from gn_modulator.utils.cache import get_global_cache, set_global_cache
from gn_modulator.utils.errors import add_error
from gn_modulator.utils.commons import get_class_from_path
from gn_modulator.utils.env import local_srid
from gn_modulator.schematisable import schematisable
from gn_modulator import DefinitionMethods

cor_type_db_schema = {
    "INTEGER": "integer",
    "VARCHAR": "string",
    "BOOLEAN": "boolean",
    "FLOAT": "number",
    "UUID": "uuid",
    "DATETIME": "datetime",
    "DATE": "date",
    "JSONB": "json",
}


class SchemaAuto:
    def insp(self):
        insp = get_global_cache(["insp"])
        if insp is None:
            insp = inspect(db.engine)
            set_global_cache(["insp"], insp)
        return insp

    def get_auto_schema(self):
        """ """
        schema_definition = self.definition

        schema_dot_table = self.sql_schema_dot_table()

        if not self.cls.c_sql_schema_dot_table_exists(schema_dot_table):
            schema_definition["properties"] = {}
            return schema_definition

        Model = schematisable(get_class_from_path(self.attr("meta.model")))
        if Model is None:
            raise SchemaAutoError("Pas de modèles trouvé pour la table {schema_dot_table}")

        properties_auto = self.autoproperties(Model, schema_definition.get("properties", {}))

        for key, property in schema_definition.get("properties", {}).items():
            if key in properties_auto:
                properties_auto[key].update(property)
            elif "type" in property:
                properties_auto[key] = property
            else:
                add_error(
                    error_msg=f"Propriété non conforme {self.schema_code()}.{key}: {property}",
                    definition_type="schema",
                    definition_code=self.schema_code(),
                    error_code="ERR_SCHEMA_AUTO",
                    file_path=DefinitionMethods.get_file_path("schema", self.schema_code()),
                )

        schema_definition["properties"] = properties_auto

        required = self.attr("required", [])

        required_auto = [
            key
            for key, property in schema_definition.get("properties", {}).items()
            if property.get("required")
        ]
        schema_definition["required"] = list(dict.fromkeys(required_auto + required))

        for elem in required_auto:
            if elem in required:
                print(
                    "elem required en doublon",
                    self,
                    {"elem": elem, "required": required, "auto": required_auto},
                )

        self.processModel(Model)

        return schema_definition

    def processModel(self, Model):
        """
        ajout d'info au niveau du modele
        default field
        TODO
        unique
        nomenclature_type ?
        """
        Model.default_fields = self.default_fields(Model)

    def autoproperties(self, Model, properties_from_definition):
        properties = {}

        sql_table_name = Model.__tablename__
        sql_schema_name = Model.__table__.schema

        # columns
        for column in Model.__table__.columns:
            if not hasattr(Model, column.key):
                continue
            column_auto = self.process_column_auto(
                column,
                sql_schema_name,
                sql_table_name,
                properties_from_definition.get(column.key, {}),
            )
            if column_auto:
                properties[column.key] = column_auto

        # column properties
        columns = [c.key for c in Model.__table__.columns]

        for k in Model.__mapper__.attrs.keys():
            col = getattr(Model, k)
            if (not isinstance(col.property, ColumnProperty)) or (k in columns):
                continue
            properties[k] = {"type": "string", "column_property": True}

        # relationships
        for relation_key, relation in inspect(Model).relationships.items():
            # if relation_key not in self.attr("meta.relations", []):
            # continue
            property = self.process_relation_auto(relation_key, relation, Model, properties)
            if property:
                properties[relation_key] = property

        return properties

    def process_relation_auto(self, relation_key, relation, Model, properties):
        # return

        if not relation.target.schema:
            return

        sql_schema_dot_table = f"{relation.target.schema}.{relation.target.name}"
        schema_code = self.cls.c_get_schema_code_from_sql_schema_dot_table(sql_schema_dot_table)
        if not schema_code:
            return
        property = {
            "type": "relation",
            "relation_type": (
                "n-1"
                if relation.direction.name == "MANYTOONE"
                else "1-n" if relation.direction.name == "ONETOMANY" else "n-n"
            ),
            "schema_code": schema_code,
            # "title": relation_key,
        }

        if property["relation_type"] == "n-n":
            property["schema_dot_table"] = f"{relation.secondary.schema}.{relation.secondary.name}"

        if property["relation_type"] == "n-1":
            # on cherche local key
            x = getattr(Model, relation_key).property.local_remote_pairs[0][0]
            property["local_key"] = x.key

        if self.definition.get("properties", {}).get(relation_key):
            property.update(self.property(relation_key))

        if schema_code == "ref_nom.nomenclature":
            if not property.get("nomenclature_type"):
                if property["relation_type"] == "n-1":
                    x = getattr(Model, relation_key)
                    y = x.property.local_remote_pairs[0][0]
                    property["nomenclature_type"] = properties[y.key]["nomenclature_type"]
                    # self.reflect_nomenclature_type(
                    # y.table.schema, y.table.name, y.key
                    # )
                if property["relation_type"] == "n-n":
                    x = getattr(Model, relation_key).property

                    for p in x.local_remote_pairs:
                        for pp in p:
                            for ppp in pp.foreign_keys:
                                if (
                                    ppp.column.table.schema == "ref_nomenclatures"
                                    and ppp.column.table.name == "t_nomenclatures"
                                ):
                                    property["nomenclature_type"] = self.reflect_nomenclature_type(
                                        pp.table.schema, pp.table.name, pp.key
                                    )

            # check si on a bien un type de nomenclature
            if not property.get("nomenclature_type") and property["relation_type"] != "1-n":
                add_error(
                    error_msg=f"nomenclature_type manquante {self.schema_code()} {relation_key}",
                    error_code="ERR_SCHEMA_AUTO_MISSING_NOMENCLATURE_TYPE",
                    definition_type="schema",
                    definition_code=self.schema_code(),
                    file_path=DefinitionMethods.get_file_path("schema", self.schema_code()),
                )

            if property.get("nomenclature_type"):
                getattr(Model, relation_key).nomenclature_type = property["nomenclature_type"]

        return property

    def process_column_auto(
        self, column, sql_schema_name, sql_table_name, property_from_definition
    ):
        type = str(column.type)
        if "VARCHAR(" in type:
            type = "VARCHAR"

        schema_type = self.cls.c_get_type(type, "sql", "definition")
        if not schema_type:
            print(
                f"{sql_schema_name}.{sql_table_name}.{column.key} : Le type sql {column.type} n'a pas de correspondance"
            )
            raise SchemaAutoError(
                f"{sql_schema_name}.{sql_table_name}.{column.key} : Le type sql {column.type} n'a pas de correspondance"
            )

        property = {**property_from_definition}

        property["type"] = property.get("type", schema_type["type"])

        if schema_type["type"] == "geometry":
            if schema_type["srid"] == -1:
                schema_type["srid"] = local_srid()
            property["srid"] = schema_type["srid"]
            property["geometry_type"] = schema_type["geometry_type"]
            property["geometry_type"] = (
                column.type.geometry_type.lower() or schema_type["geometry_type"]
            )

        # primary_key

        if column.primary_key:
            property["primary_key"] = True

        # patch pourris id_nomenclature_type_site id_module monitoring TBaseSites
        if property.get("foreign_key") and not column.foreign_keys:
            setattr(column, "foreign_key", True)

            if property.get("schema_code") == "ref_nom.nomenclature":
                nomenclature_type = property_from_definition.get(
                    "nomenclature_type"
                ) or self.reflect_nomenclature_type(sql_schema_name, sql_table_name, column.key)

                property["nomenclature_type"] = nomenclature_type
                column.nomenclature_type = nomenclature_type

        # foreign_keys

        for foreign_key in column.foreign_keys:
            # key = foreign_key.target_fullname.split(".")[-1]
            schema_dot_table = ".".join(foreign_key._table_key().split("."))
            schema_code = self.cls.c_get_schema_code_from_sql_schema_dot_table(schema_dot_table)
            if not schema_code:
                # TODO avec des schema non encore crées ??
                continue
            property["foreign_key"] = True
            property["schema_code"] = schema_code

            if schema_code == "ref_nom.nomenclature":
                # nomenclature_type
                nomenclature_type = property_from_definition.get(
                    "nomenclature_type"
                ) or self.reflect_nomenclature_type(sql_schema_name, sql_table_name, column.key)
                property["nomenclature_type"] = nomenclature_type
                column.nomenclature_type = nomenclature_type

        # commentaires
        # if column.comment:
        # property["description"] = column.comment

        column_info = self.cls.c_get_column_info(sql_schema_name, sql_table_name, column.key) or {}

        # pour être requis
        # etre nullable
        # ne pas être que pk (fkpk non nullable ok)
        # pas de default
        # meta_date ??
        condition_required = (
            (not column_info.get("nullable", True))
            and (not (column.primary_key and not property.get("foreign_key")))
            and (column_info.get("default") is None)
            and (column.key != "meta_create_date")
        )

        if column_info.get("geometry_type"):
            property["geometry_type"] = column_info["geometry_type"].lower()

        if condition_required:
            property["required"] = True

        return property

    def get_check_constraints(self, sql_schema_name, sql_table_name):
        check_constraints = get_global_cache(["check_contraints", sql_schema_name, sql_table_name])
        if check_constraints is None:
            check_constraints = self.insp().get_check_constraints(
                sql_table_name, schema=sql_schema_name
            )
            set_global_cache(
                ["check_contraints", sql_schema_name, sql_table_name], check_constraints
            )
        return check_constraints

    def reflect_nomenclature_type(self, sql_schema_name, sql_table_name, column_key):
        """
        va chercher les type de nomenclature depuis les contraintes 'check_nomenclature_type'
        """
        check_constraints = self.get_check_constraints(sql_schema_name, sql_table_name)
        for check_constraint in check_constraints:
            sqltext = check_constraint["sqltext"]
            s_test1 = f"ref_nomenclatures.check_nomenclature_type_by_mnemonique({column_key}, '"
            s_test2 = "'::character varying)"
            if s_test1 in sqltext:
                nomenclature_type = sqltext.replace(s_test1, "").replace(s_test2, "")
                return nomenclature_type
