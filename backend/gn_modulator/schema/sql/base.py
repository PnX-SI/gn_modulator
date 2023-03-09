"""
    SchemaMethods : SQL

    SQL text production methods for schema
"""

import sqlparse
from sqlalchemy import inspect
from geonature.utils.env import db
from gn_modulator.utils.cache import get_global_cache, set_global_cache
from gn_modulator.utils.commons import get_class_from_path
from ..errors import (
    SchemaProcessedPropertyError,
)


class SchemaSqlBase:
    @classmethod
    def auto_sql_schemas_dot_tables(cls):
        auto_sql_schemas_dot_tables = []
        for schema_code in cls.schema_codes():
            schema_definition = get_global_cache(["schema", schema_code, "definition"])
            if not schema_definition["meta"].get("autoschema"):
                continue

            Model = get_class_from_path(schema_definition["meta"]["model"])
            table_name = Model.__tablename__
            table_schema = Model.__table__.schema
            auto_sql_schemas_dot_tables.append(f"{table_schema}.{table_name}")

        return auto_sql_schemas_dot_tables

    @classmethod
    def get_tables(cls):
        if tables := get_global_cache(["schema_dot_tables"]):
            return tables

        sql_txt_tables = f"""
        SELECT
        concat(t.table_schema, '.', t.table_name)
        FROM
            information_schema.tables t
        WHERE
            CONCAT(t.table_schema, '.', t.table_name)  IN ('{"', '".join(cls.auto_sql_schemas_dot_tables())}')

        """
        res = cls.c_sql_exec_txt(sql_txt_tables)
        tables = [r[0] for r in res]
        set_global_cache(["schema_dot_tables"], tables)
        return tables

    @classmethod
    def get_table_columns(cls, schema_dot_table):
        table_schema = schema_dot_table.split(".")[0]
        table_name = schema_dot_table.split(".")[1]
        sql_txt_table_columns = f"""
        SELECT
            column_name
        FROM
            information_schema.columns c
        WHERE
            c.table_schema = '{table_schema}'
            AND c.table_name = '{table_name}'
        """
        res = cls.c_sql_exec_txt(sql_txt_table_columns)

        columns = []
        for r in res:
            columns.append(r[0])

        return columns

    @classmethod
    def get_columns_info(cls):
        if get_global_cache(["columns"]):
            return

        # on récupère les info des colonnes depuis information_schema.columns
        sql_txt_get_columns_info = f"""
SELECT
  c.table_schema,
  c.table_name,
  column_name,
  column_default,
  is_nullable
FROM
  information_schema.columns c
WHERE
    CONCAT(c.table_schema, '.', c.table_name)  IN ('{"', '".join(cls.auto_sql_schemas_dot_tables())}')
"""
        res = cls.c_sql_exec_txt(sql_txt_get_columns_info)

        columns_info = {}

        for r in res:
            schema_name = r[0]
            table_name = r[1]
            column_name = r[2]
            columns_info[schema_name] = columns_info.get(schema_name) or {}
            columns_info[schema_name][table_name] = columns_info[schema_name].get(table_name) or {}

            column_info = {"default": r[3], "nullable": r[4] == "YES"}
            columns_info[schema_name][table_name][column_name] = column_info
            # set_global_cache(["columns", schema_name, table_name, column_name], column_info)
            set_global_cache(["columns"], columns_info)

    @classmethod
    def get_column_info(cls, schema_name, table_name, column_name):
        cls.get_columns_info()
        return get_global_cache(["columns", schema_name, table_name, column_name])

    def is_nullable(self, column_name):
        return (
            self.cls.get_column_info(self.sql_schema_name(), self.sql_table_name(), column_name)[
                "nullable"
            ]
            if self.autoschema()
            else getattr(self.Model().__table__.columns, column_name).nullable
        )

    @classmethod
    def sql_txt(cls, query):
        return str(query.statement.compile(compile_kwargs={"literal_binds": True}))

    @classmethod
    def format_sql(cls, sql_txt):
        return sqlparse.format(sql_txt.replace("%%", "%"), reindent=True, keywordcase="upper")

    @classmethod
    def pprint_sql(cls, sql_txt):
        print(cls.format_sql(sql_txt))

    def get_sql_type(self, column_def, cor_table=False, required=False):
        field_type = column_def.get("type")

        sql_type = self.cls.c_get_type(field_type, "definition", "sql")["type"]
        if column_def.get("primary_key") and not cor_table:
            sql_type = "SERIAL NOT NULL"

        if field_type == "geometry":
            sql_type = "GEOMETRY({}, {})".format(
                column_def.get("geometry_type", "GEOMETRY").upper(), column_def["srid"]
            )

        if not sql_type:
            raise SchemaProcessedPropertyError(
                "Property type {} in processed_properties but not managed yet for SQL processing".format(
                    field_type
                )
            )

        if required and ("NOT NULL" not in sql_type):
            sql_type += " NOT NULL"

        return sql_type

    def sql_default(self, column_def):
        if column_def.get("default") is None:
            return None
        if column_def["type"] == "uuid":
            # PATCH DEBUG
            return "public.uuid_generate_v4()"
            return "uuid_generate_v4()"

    def sql_schema_name(self):
        """
        from meta.sql_schema_name or id
        """
        return self.sql_schema_dot_table().split(".")[0]

    def sql_table_name(self):
        """
        from meta.sql_table_name or id
        """
        return self.sql_schema_dot_table().split(".")[1]

    def sql_schema_dot_table(self):
        return self.cls.c_get_sql_schema_dot_table_from_definition(self.schema_code())

    @classmethod
    def c_get_sql_schema_dot_table_from_definition(cls, schema_code):
        definition = get_global_cache(["schema", schema_code, "definition"])
        sql_schema_dot_table = definition["meta"].get("sql_schema_dot_table")

        if sql_schema_dot_table is not None:
            return sql_schema_dot_table

        Model = get_class_from_path(definition["meta"].get("model"))
        return f"{Model.__table__.schema}.{Model.__tablename__}"

    @classmethod
    def c_get_schema_code_from_sql_schema_dot_table(cls, sql_schema_dot_table):
        for schema_code in cls.schema_codes():
            if cls.c_get_sql_schema_dot_table_from_definition(schema_code) == sql_schema_dot_table:
                return schema_code

    @classmethod
    def c_sql_schema_dot_table_exists(cls, sql_schema_dot_table):
        sql_schema_name = sql_schema_dot_table.split(".")[0]
        sql_table_name = sql_schema_dot_table.split(".")[1]
        return cls.c_sql_table_exists(sql_schema_name, sql_table_name)

    @classmethod
    def c_sql_table_exists(cls, sql_schema_name, sql_table_name):
        return f"{sql_schema_name}.{sql_table_name}".lower() in cls.get_tables()

    @classmethod
    def c_sql_schema_exists(cls, sql_schema_name):
        return sql_schema_name in inspect(db.engine).get_schema_names()

    def sql_schema_exists(self):
        """
        check if sql schema exists
        """
        return self.cls.c_sql_schema_exists(self.sql_schema_name())

    def sql_table_exists(self):
        """
        check if sql table exists
        """
        return self.cls.c_sql_table_exists(self.sql_schema_name(), self.sql_table_name())

    def sql_txt_create_schema(self):
        """
        Create schema sql schema
        """
        txt = "CREATE SCHEMA  IF NOT EXISTS {};".format(self.sql_schema_name())
        return txt

    def sql_txt_drop_schema(self):
        """
        Drop schema sql schema

        Jamais de drop cascade !!!!!!!
        """

        txt = "DROP SCHEMA {};".format(self.sql_schema_name())
        return txt

    def sql_processing(self):
        """
        Variable meta
            - pour authoriser l'execution de script sql pour le schema
            - par defaut à False
        """
        return self.attr("meta.sql_processing", False)

    @classmethod
    def c_sql_exec_txt(cls, txt):
        """
        - exec txt as sql
        - remove empty or comments or empty lines and exec sql
          - db.engine.execute doesn't process sql text with comments
        """

        txt_no_comment = "\n".join(
            filter(lambda l: (l and not l.strip().startswith("--")), txt.split("\n"))
        )
        return db.session.execute(txt_no_comment)

    def sql_txt_drop_table(self):
        """
        code sql qui permet de supprimer la table du schema
        """
        txt = ""

        txt += "DROP TABLE {}.{};".format(self.sql_schema_name(), self.sql_table_name())

        return txt

    def sql_txt_process(self, processed_schema_codes=[]):
        """
        process all sql for a schema
        """

        clear_global_cache(["sql_table"])
        if not self.sql_processing():
            processed_schema_codes.append(self.schema_code())
            return "", processed_schema_codes

        schema_codes_to_process = []
        for name in self.dependencies():
            sm = self.cls(name)
            if (
                # si la creation de sql est permise pour ce schema
                sm.sql_processing()
                # et si la table n'existe pas déjà
                and (not sm.sql_table_exists())
                # et si le code sql pour ce schema ne vient pas d'être crée par un appel précédent à sql_txt_process
                and (name not in processed_schema_codes)
            ):
                schema_codes_to_process.append(name)

        txt = "-- process schema : {}\n".format(self.schema_code())
        if schema_codes_to_process:
            txt += "--\n-- and dependencies : {}\n".format(", ".join(schema_codes_to_process))
        txt += "\n\n"

        if self.schema_code() not in processed_schema_codes:
            schema_codes_to_process.insert(0, self.schema_code())

        # schemas
        sql_schema_names = []
        for name in schema_codes_to_process:
            sm = self.cls(name)
            if sm.sql_schema_name() not in sql_schema_names and not sm.sql_schema_exists():
                sql_schema_names.append(sm.sql_schema_name())

        for sql_schema_name in sql_schema_names:
            txt += "---- sql schema {sql_schema_name}\n\n".format(sql_schema_name=sql_schema_name)
            txt += "CREATE SCHEMA IF NOT EXISTS {sql_schema_name};\n\n".format(
                sql_schema_name=sql_schema_name
            )

        # actions
        for action in [
            "sql_txt_create_table",
            "slq_txt_unique_key_constraint",
            "sql_txt_primary_key_constraints",
            "sql_txt_foreign_key_constraints",
            "sql_txt_nomenclature_type_constraints",
            "sql_txt_process_correlations",
            "sql_txt_process_triggers",
            "sql_txt_process_index",
        ]:
            for name in schema_codes_to_process:
                sm = self.cls(name)
                txt_action = getattr(sm, action)()
                if txt_action:
                    txt += "{}\n".format(txt_action)

        return txt, processed_schema_codes + schema_codes_to_process
