"""
    sql table
"""

from gn_modules.utils.cache import get_global_cache, set_global_cache


class SchemaSqlTable:
    """
    sql table and correlation table
    """

    def sql_txt_process_correlations(self):
        """
        fonction qui cree les table de correlation associée
        """

        txt = ""
        for key, relation_def in self.relationships().items():
            txt += self.sql_txt_process_correlation(key, relation_def)

        return txt

    def sql_txt_process_correlation(self, key, relation_def):
        """
        fonction qui cree les table de correlation associée
        """

        txt = ""

        if not relation_def["relation_type"] == "n-n":
            return txt

        relation_schema_dot_table = (
            relation_def.get("schema_dot_table")
            or self.cls(relation_def.get("cor_schema_code")).sql_schema_dot_table()
        )

        if get_global_cache(["sql_table", relation_schema_dot_table]):
            return txt

        set_global_cache(["sql_table", relation_schema_dot_table], True)

        local_key = self.pk_field_name()
        local_key_type = self.get_sql_type(self.column(local_key), cor_table=True, required=True)
        local_table_name = self.sql_table_name()
        local_schema_code = self.sql_schema_name()

        relation = self.cls(relation_def["schema_code"])
        foreign_key = relation.pk_field_name()
        foreign_key_type = relation.get_sql_type(
            relation.column(foreign_key), cor_table=True, required=True
        )
        foreign_table_name = relation.sql_table_name()
        foreign_schema_code = relation.sql_schema_name()

        cor_schema_dot_table = relation_schema_dot_table
        cor_schema_code = cor_schema_dot_table.split(".")[0]
        cor_table_name = cor_schema_dot_table.split(".")[1]

        txt_args = {
            "cor_schema_code": cor_schema_code,
            "cor_table_name": cor_table_name,
            "cor_schema_dot_table": cor_schema_dot_table,
            "local_key": local_key,
            "local_key_type": local_key_type,
            "local_schema_code": local_schema_code,
            "local_table_name": local_table_name,
            "foreign_key": foreign_key,
            "foreign_key_type": foreign_key_type,
            "foreign_schema_code": foreign_schema_code,
            "foreign_table_name": foreign_table_name,
        }

        txt += """-- cor {cor_schema_dot_table}

CREATE TABLE IF NOT EXISTS {cor_schema_dot_table} (
    {local_key} {local_key_type} NOT NULL,
    {foreign_key} {foreign_key_type} NOT NULL
);


---- {cor_schema_dot_table} primary keys contraints

ALTER TABLE {cor_schema_dot_table}
    ADD CONSTRAINT pk_{cor_schema_code}_{cor_table_name}_{local_key}_{foreign_key} PRIMARY KEY ({local_key}, {foreign_key});

---- {cor_schema_dot_table} foreign keys contraints

ALTER TABLE {cor_schema_dot_table}
    ADD CONSTRAINT fk_{cor_schema_code}_{cor_table_name}_{local_key} FOREIGN KEY ({local_key})
    REFERENCES {local_schema_code}.{local_table_name} ({local_key})
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE {cor_schema_dot_table}
    ADD CONSTRAINT fk_{cor_schema_code}_{cor_table_name}_{foreign_key} FOREIGN KEY ({foreign_key})
    REFERENCES {foreign_schema_code}.{foreign_table_name} ({foreign_key})
    ON UPDATE CASCADE ON DELETE CASCADE;
""".format(
            **txt_args
        )

        if relation_def.get("nomenclature_type"):
            txt += self.sql_txt_nomenclature_type_constraint(
                txt_args["cor_schema_code"],
                txt_args["cor_table_name"],
                "id_nomenclature",
                relation_def.get("nomenclature_type"),
            )
        return txt

    def sql_txt_create_table(self):
        """
        fonction qui produit le texte sql pour la creation d'une table

        types :
            - integer -> INTEGER ou SERIAL
            - string -> VARCHAR

        contraintes :
            - pk_field_name

        TODO
        - fk ?? etape 2
        """

        txt = ""

        txt = """---- table {sql_schema_name}.{sql_table_name}

CREATE TABLE {sql_schema_name}.{sql_table_name} (""".format(
            sql_schema_name=self.sql_schema_name(), sql_table_name=self.sql_table_name()
        )

        # liste des champs
        for key, column_def in self.columns().items():

            if column_def.get("column_property") is not None:
                continue

            sql_type = self.get_sql_type(column_def, required=self.is_required(key))
            sql_default = self.sql_default(column_def)
            txt += "\n    {} {}{},".format(
                key,
                sql_type,
                " NOT NULL DEFAULT {}".format(sql_default) if sql_default else "",
            )

        # TODO relations et clés étrangères

        # finalisation
        #  - suppresion de la dernière virgule
        #  - fermeture de la parenthèse
        #  - point virgule final
        txt = txt[:-1] + "\n);\n\n"

        txt += self.sql_txt_comments()

        return txt

    def sql_txt_comments(self):

        txt = ""

        for key, column_def in self.columns().items():

            if column_def.get("description") is None:
                continue
            txt += "COMMENT ON COLUMN {sql_schema_name}.{sql_table_name}.{key} IS '{description}';\n".format(
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name(),
                key=key,
                description=column_def["description"].replace("'", "''"),
            )

        return txt
