from gn_modulator import SchemaMethods
from .utils import ImportMixinUtils


class ImportMixinProcess(ImportMixinUtils):
    def process_view(self, keys=None):
        from_table = self.tables["raw"]
        dest_table = self.tables["process"] = self.table_name("process")

        self.sql["process_view"] = self.sql_process_view(from_table, dest_table, keys)

        try:
            SchemaMethods.c_sql_exec_txt(self.sql["process_view"])
        except Exception as e:
            self.add_error(
                code="ERR_IMPORT_PROCESS_CREATE_VIEW",
                msg=f"La vue de process n'a pas être crée : {str(e)}",
            )
            return

        self.count_and_check_table("process", dest_table)

    def sql_process_view(self, from_table, dest_table, keys=None):
        """
        requete pour créer une vue qui résoud les clé
        """

        sm = SchemaMethods(self.schema_code)

        v_columns = []
        v_joins = []

        from_table_columns = self.get_table_columns(from_table)

        columns = list(
            filter(
                lambda x: (
                    x in keys
                    if keys is not None
                    else sm.is_column(x) and not sm.property(x).get("primary_key")
                ),
                from_table_columns,
            )
        )

        solved_keys = {}

        for index, key in enumerate(columns):
            txt_column, v_join = self.process_column_import_view(index, key)
            if txt_column:
                # TODO n-n ici ????
                if sm.has_property(key) and sm.property(key).get("relation_type") == "n-n":
                    rel = SchemaMethods(sm.property(key)["schema_code"])
                    v_columns.append(f"{txt_column.split('.')[0]}.{rel.pk_field_name()}")
                else:
                    v_columns.append(f"{txt_column} AS {key}")
            solved_keys[key] = txt_column
            v_joins += v_join

        txt_pk_column, v_join = self.resolve_key(
            self.schema_code, sm.pk_field_name(), alias_join_base="j_pk", solved_keys=solved_keys
        )
        v_columns.append(txt_pk_column)
        v_joins += v_join

        txt_columns = ",\n    ".join(v_columns)
        txt_joins = "\n".join(v_joins)

        # TODO rendre id_digitiser parametrable ?
        txt_id_digitiser = ""
        if self.id_digitiser:
            for key in ["id_digitiser", "id_digitizer"]:
                if SchemaMethods(self.schema_code).has_property(key):
                    txt_id_digitiser = f"{self.id_digitiser} AS {key},"
                    break

        return f"""DROP VIEW IF EXISTS {dest_table} CASCADE;
CREATE VIEW {dest_table} AS
SELECT
    id_import,
    {txt_id_digitiser}
    {txt_columns}
FROM {from_table} t
{txt_joins};
"""

    def resolve_key(
        self, schema_code, key, index=None, alias_main="t", alias_join_base="j", solved_keys={}
    ):
        """
        compliqué
        crée le txt pour
            le champs de la colonne qui doit contenir la clé
            la ou les jointures nécessaire pour résoudre la clé
        """
        sm = SchemaMethods(schema_code)

        alias_join = alias_join_base if index is None else f"{alias_join_base}_{index}"

        txt_column = f"{alias_join}.{sm.pk_field_name()}"

        unique = sm.attr("meta.unique")
        v_join = []

        # resolution des cles si besoins

        # couf pour permttre de faire les liens entre les join quand il y en a plusieurs
        link_joins = {}
        for index_unique, k_unique in enumerate(unique):
            var_key = self.var_key(
                schema_code, key, k_unique, index_unique, link_joins, alias_main
            )
            if sm.property(k_unique).get("foreign_key"):
                if k_unique in solved_keys:
                    link_joins[k_unique] = solved_keys[k_unique]
                else:
                    rel = SchemaMethods(sm.property(k_unique)["schema_code"])
                    txt_column_join, v_join_inter = self.resolve_key(
                        rel.schema_code(),
                        var_key,
                        index=index_unique,
                        alias_main=alias_join,
                        alias_join_base=alias_join,
                    )
                    v_join += v_join_inter

                    link_joins[k_unique] = f"{alias_join}_{index_unique}.{rel.pk_field_name()}"

        # creation des joins avec les conditions
        v_join_on = []

        for index_unique, k_unique in enumerate(unique):
            var_key = self.var_key(
                schema_code, key, k_unique, index_unique, link_joins, alias_main
            )
            # !!!(SELECT (NULL = NULL) => NULL)
            cast = "::TEXT"  # if var_type != main_type else ''
            txt_join_on = (
                f"{alias_join}.{k_unique}{cast} = {var_key}{cast}"
                if not sm.is_nullable(k_unique) or sm.is_required(k_unique)
                else f"({alias_join}.{k_unique}{cast} = {var_key}{cast} OR ({alias_join}.{k_unique} IS NULL AND {var_key} IS NULL))"
                # else f"({var_key} IS NOT NULL) AND ({alias_join}.{k_unique} = {var_key})"
            )
            v_join_on.append(txt_join_on)

        txt_join_on = "\n        AND ".join(v_join_on)
        txt_join = f"LEFT JOIN {sm.sql_schema_dot_table()} {alias_join} ON\n      {txt_join_on}"

        v_join.append(txt_join)

        return txt_column, v_join

    def var_key(self, schema_code, key, k_unique, index_unique, link_joins, alias_main):
        """
        TODO à clarifier
        """
        sm = SchemaMethods(schema_code)

        if key is None:
            return f"{alias_main}.{k_unique}"

        if link_joins.get(k_unique):
            return link_joins[k_unique]

        if "." in key:
            return key

        if len(sm.attr("meta.unique", [])) <= 1:
            return f"{alias_main}.{key}"

        return f"SPLIT_PART({alias_main}.{key}, '|', { index_unique + 1})"

    def process_column_import_view(self, index, key):
        """
        process column for processed view
        """
        sm = SchemaMethods(self.schema_code)
        if not sm.has_property(key):
            return key, []

        property = sm.property(key)

        if property.get("foreign_key"):
            return self.resolve_key(property["schema_code"], key, index)

        if property.get("relation_type") == "n-n":
            return self.resolve_key(property["schema_code"], key, index)

            # txt_column, v_join = rel.resolve_key(key, index)
            # return f"{txt_column.split('.')[0]}.{rel.pk_field_name()}", v_join

        return f"t.{key}", []
