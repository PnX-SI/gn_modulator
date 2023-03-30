"""
    AutoSchemas
"""
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.engine import reflection
from geonature.utils.env import db
from .errors import SchemaAutoError
from gn_modulator.utils.cache import get_global_cache, set_global_cache
from gn_modulator.utils.commons import get_class_from_path
from gn_modulator.utils.env import local_srid

cor_type_db_schema = {
    "INTEGER": "integer",
    "VARCHAR": "string",
    "BOOLEAN": "boolean",
    "FLOAT": "number",
    "UUID": "uuid",
    "DATETIME": "datetime",
    "DATE": "date",
}


class SchemaAuto:
    def insp(self):
        insp = get_global_cache(["insp"])
        if insp is None:
            insp = reflection.Inspector.from_engine(db.engine)
            set_global_cache(["insp"], insp)
        return insp

    def autoschema(self):
        """
        boolean pour savoir si on calcule le schema automatiquement
        """
        return self.attr("meta.autoschema")

    def get_autoschema(self):
        """
        combine definition schema & autoschema
        """
        schema_definition = self.definition

        schema_dot_table = self.sql_schema_dot_table()

        if not self.cls.c_sql_schema_dot_table_exists(schema_dot_table):
            schema_definition["properties"] = {}
            return schema_definition

        Model = get_class_from_path(self.attr("meta.model"))
        if Model is None:
            raise SchemaAutoError(
                "Pas de modèles trouvé pour la table {}".format(schema_dot_table)
            )

        properties_auto = self.autoproperties(Model)

        for key, property in schema_definition.get("properties", {}).items():
            if key in properties_auto:
                properties_auto[key].update(property)
            else:
                properties_auto[key] = property

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
        return schema_definition

    def autoproperties(self, Model):
        properties = {}

        sql_table_name = Model.__tablename__
        sql_schema_name = Model.__table__.schema

        # columns
        for column in Model.__table__.columns:
            if not hasattr(Model, column.key):
                continue
            column_auto = self.process_column_auto(column, sql_schema_name, sql_table_name)
            if column_auto:
                properties[column.key] = column_auto

        # column properties
        columns = [c.key for c in Model.__table__.columns]

        for k in Model.__mapper__.attrs.keys():
            col = getattr(Model, k)
            if (not isinstance(col.property, ColumnProperty)) or (k in columns):
                continue
            properties[k] = {
                "type": "string",
                "is_column_property": True
                # "column_property": "label",
                # "title": k,
            }

        # relationships
        for relation_key, relation in inspect(Model).relationships.items():
            # if relation_key not in self.attr("meta.relations", []):
            # continue
            property = self.process_relation_auto(relation_key, relation)
            if property:
                properties[relation_key] = property

        return properties

    def process_relation_auto(self, relation_key, relation):
        # return

        if not relation.target.schema:
            return

        sql_schema_dot_table = "{}.{}".format(relation.target.schema, relation.target.name)
        schema_code = self.cls.c_get_schema_code_from_sql_schema_dot_table(sql_schema_dot_table)
        if not schema_code:
            return
        property = {
            "type": "relation",
            "relation_type": (
                "n-1"
                if relation.direction.name == "MANYTOONE"
                else "1-n"
                if relation.direction.name == "ONETOMANY"
                else "n-n"
            ),
            "schema_code": schema_code,
            # "title": relation_key,
        }

        if property["relation_type"] == "n-n":
            property["schema_dot_table"] = "{}.{}".format(
                relation.secondary.schema, relation.secondary.name
            )

        if self.definition.get("properties", {}).get(relation_key):
            property.update(self.property(relation_key))

        return property

    def process_column_auto(self, column, sql_schema_name, sql_table_name):
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

        property = {
            "type": schema_type["type"],
            # "title": column.key
        }

        if schema_type["type"] == "geometry":
            if schema_type["srid"] == -1:
                schema_type["srid"] = local_srid()
                # schema_type["srid"] = db.engine.execute(
                #     f"SELECT FIND_SRID('{sql_schema_name}', '{sql_table_name}', '{column.key}')"
                # ).scalar()
            property["srid"] = schema_type["srid"]
            property["geometry_type"] = schema_type["geometry_type"]
            property["geometry_type"] = (
                column.type.geometry_type.lower() or schema_type["geometry_type"]
            )

        # primary_key

        if column.primary_key:
            property["primary_key"] = True

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
                nomenclature_type = self.reflect_nomenclature_type(
                    sql_schema_name, sql_table_name, column.key
                )
                property["nomenclature_type"] = nomenclature_type
                # property.pop('foreign_key')

        # commentaires
        # if column.comment:
        # property["description"] = column.comment

        column_info = self.cls.get_column_info(sql_schema_name, sql_table_name, column.key) or {}

        condition_required = (
            (not column_info.get("nullable", True))
            and (not column.primary_key)
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
            s_test1 = "ref_nomenclatures.check_nomenclature_type_by_mnemonique({}, '".format(
                column_key
            )
            s_test2 = "'::character varying)"
            if s_test1 in sqltext:
                nomenclature_type = sqltext.replace(s_test1, "").replace(s_test2, "")
                return nomenclature_type
