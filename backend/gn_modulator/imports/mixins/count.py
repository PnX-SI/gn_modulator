from gn_modulator import SchemaMethods
from .utils import ImportMixinUtils


class ImportMixinCount(ImportMixinUtils):
    def process_count(self):
        self.count_insert()
        self.count_update()
        self.res["nb_unchanged"] = (
            self.res["nb_process"] - self.res["nb_insert"] - self.res["nb_update"]
        )

    def update_condition_columns(self):
        sm = SchemaMethods(self.schema_code)
        columns = self.get_table_columns(self.tables["raw"])
        return list(
            map(
                lambda x: f"(t.{x}::TEXT IS DISTINCT FROM a.{x}::TEXT)",
                filter(
                    lambda x: sm.is_column(x) and not sm.property(x).get("primary_key"),
                    columns,
                ),
            )
        )

    def with_rel(self, key):
        sm = SchemaMethods(self.schema_code)
        pk = sm.pk_field_name()
        rel = SchemaMethods(sm.property(key)["schema_code"])
        rel_pk = rel.pk_field_name()
        cor_table = sm.property(key)["schema_dot_table"]

        return f"""process_{key} AS (
        SELECT
            {pk},
            ARRAY_AGG({rel_pk}) AS a
            FROM {self.tables['relations'][key]['process']}
            GROUP BY {pk}
    ), cor_{key} AS (
        SELECT
            {pk},
            ARRAY_AGG({rel_pk}) AS a
            FROM {cor_table}
            GROUP BY {pk}
    )"""

    def join_rel(self, key):
        sm = SchemaMethods(self.schema_code)
        pk = sm.pk_field_name()

        return f"""    LEFT JOIN process_{key} 
        ON process_{key}.{pk} = t.{pk}
    LEFT JOIN cor_{key}
        ON cor_{key}.{pk} = t.{pk}"""

    def update_condition_rel(self, key):
        return f"""process_{key}.a IS DISTINCT FROM cor_{key}.a"""

    def update_condition_relations(self):
        sm = SchemaMethods(self.schema_code)
        columns = self.get_table_columns(self.tables["raw"])
        relations = list(
            filter(
                lambda x: sm.has_property(x) and sm.property(x).get("relation_type") == "n-n",
                columns,
            )
        )
        withs_rel = list(map(lambda x: self.with_rel(x), relations))
        joins_rel = list(map(lambda x: self.join_rel(x), relations))
        update_conditions_rel = list(map(lambda x: self.update_condition_rel(x), relations))

        return withs_rel, joins_rel, update_conditions_rel

    def sql_nb_update(self):
        sm = SchemaMethods(self.schema_code)

        update_conditions_columns = self.update_condition_columns()
        withs_rel, joins_rel, update_condition_relations = self.update_condition_relations()

        txt_update_conditions = (
            "" + "\n    OR ".join(update_conditions_columns + update_condition_relations) + ""
        )

        withs_rel_txt = ""
        joins_rel_txt = ""
        if len(withs_rel):
            withs_rel_txt = "    WITH " + "\n,".join(withs_rel)
            joins_rel_txt = "\n".join(joins_rel)

        return f"""{withs_rel_txt}
    SELECT
        COUNT(*)
    FROM {sm.sql_schema_dot_table()} t
    JOIN {self.tables['process']} a
        ON a.{sm.pk_field_name()} = t.{sm.pk_field_name()}
{joins_rel_txt}
    WHERE {txt_update_conditions}
;
"""

    def count_update(self):
        self.sql["nb_update"] = self.sql_nb_update()
        try:
            self.res["nb_update"] = SchemaMethods.c_sql_exec_txt(self.sql["nb_update"]).scalar()
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_UPDATE_COUNT",
                msg=f"Erreur lors du comptage du nombre d'update: {str(e)}",
            )
        return

    def count_insert(self):
        from_table = self.tables["process"]
        sm = SchemaMethods(self.schema_code)
        self.sql[
            "nb_insert"
        ] = f"SELECT COUNT(*) FROM {from_table} WHERE {sm.pk_field_name()} IS NULL"

        try:
            self.res["nb_insert"] = SchemaMethods.c_sql_exec_txt(self.sql["nb_insert"]).scalar()
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_INSERT_COUNT",
                msg=f"Erreur lors du comptage du nombre d'insert: {str(e)}",
            )
            return
