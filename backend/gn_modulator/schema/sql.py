"""
    SchemaMethods : SQL

    SQL text production methods for schema
"""

import sqlparse
import sqlalchemy as sa
from geonature.utils.env import db
from gn_modulator.utils.cache import get_global_cache, set_global_cache
from gn_modulator.utils.commons import get_class_from_path


class SchemaSql:
    @classmethod
    def auto_sql_schemas_dot_tables(cls):
        auto_sql_schemas_dot_tables = []
        for schema_code in cls.schema_codes():
            schema_definition = get_global_cache(["schema", schema_code, "definition"])

            Model = get_class_from_path(schema_definition["meta"]["model"])
            table_name = Model.__tablename__
            table_schema = Model.__table__.schema
            auto_sql_schemas_dot_tables.append(f"{table_schema}.{table_name}")

        return auto_sql_schemas_dot_tables

    @classmethod
    def get_tables(cls):
        tables = get_global_cache(["schema_dot_tables"])
        if tables:
            return tables

        sql_txt_tables = f"""
        WITH tables AS (
            SELECT
                CONCAT(t.table_schema, '.', t.table_name) AS schema_dot_table
            FROM information_schema.tables t
            UNION
            SELECT
                oid::regclass::text AS schema_dot_table
            FROM   pg_class
            WHERE  relkind = 'm'
        )
        SELECT
            schema_dot_table
        FROM tables
        WHERE schema_dot_table  IN ('{"', '".join(cls.auto_sql_schemas_dot_tables())}')
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
    is_nullable,
    DATA_TYPE AS TYPE,
    gc.TYPE AS geometry_type
FROM
    information_schema.columns c
LEFT JOIN GEOMETRY_COLUMNS GC ON
    c.TABLE_SCHEMA = GC.F_TABLE_SCHEMA
    AND c.TABLE_NAME= GC.F_TABLE_NAME
    AND c.COLUMN_NAME = gc.F_GEOMETRY_COLUMN 
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

            column_info = {
                "default": r[3],
                "nullable": r[4] == "YES",
                "type": r[5],
                "geometry_type": r[6],
            }
            columns_info[schema_name][table_name][column_name] = column_info
            # set_global_cache(["columns", schema_name, table_name, column_name], column_info)
            set_global_cache(["columns"], columns_info)

    @classmethod
    def c_get_column_info(cls, schema_name, table_name, column_name):
        cls.get_columns_info()
        return get_global_cache(["columns", schema_name, table_name, column_name])

    def get_column_info(self, column_name):
        self.cls.get_columns_info()
        return get_global_cache(
            ["columns", self.sql_schema_name(), self.sql_table_name(), column_name]
        )

    def is_nullable(self, column_name):
        return self.get_column_info(column_name)["nullable"]

    @classmethod
    def pretty_sql(cls, query):
        return str(query.statement.compile(compile_kwargs={"literal_binds": True}))

    @classmethod
    def format_sql(cls, sql_txt):
        return sqlparse.format(sql_txt.replace("%%", "%"), reindent=True, keywordcase="upper")

    @classmethod
    def pprint_sql(cls, sql_txt):
        print(cls.format_sql(sql_txt))

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

    def sql_table_exists(self):
        """
        check if sql table exists
        """
        return self.cls.c_sql_table_exists(self.sql_schema_name(), self.sql_table_name())

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
        return db.session.execute(sa.text(txt_no_comment))
