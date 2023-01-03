"""
    SchemaSqlConstraints
"""

from ..errors import SchemaSqlError


class SchemaSqlConstraint:
    """
    methods pour gerer les contraintes
    """

    def slq_txt_unique_key_constraint(self):
        """ """
        uniques = self.attr("meta.unique")

        if uniques is None:
            return ""

        txt = "\nALTER TABLE {} ADD CONSTRAINT unique_{}_{} UNIQUE({});".format(
            self.sql_schema_dot_table(),
            self.sql_schema_dot_table().replace(".", "_"),
            "_".join(uniques),
            ", ".join(uniques),
        )

        return txt

    def sql_txt_primary_key_constraints(self):
        """
        créé la containte de clé(s) primaire(s)
        """

        #  - clés primaires

        pk_field_names = self.pk_field_names()

        if not pk_field_names:
            raise SchemaSqlError(
                "Il n'y a pas de clé primaire définie pour le schema {sql_schema} {sql_table}"
            )

        return """---- {sql_schema_code}.{sql_table_name} primary key constraint

ALTER TABLE {sql_schema_code}.{sql_table_name}
    ADD CONSTRAINT pk_{sql_schema_code}_{sql_table_name}_{pk_keys_dash} PRIMARY KEY ({pk_keys_commas});

""".format(
            sql_schema_code=self.sql_schema_code(),
            sql_table_name=self.sql_table_name(),
            pk_keys_dash="_".join(pk_field_names),
            pk_keys_commas=", ".join(pk_field_names),
        )

    def sql_txt_foreign_key_constraints(self):
        """
        créé les containtes de clés étrangères
        """
        txt = ""

        for key, column_def in self.columns().items():

            if not column_def.get("foreign_key"):
                continue

            relation = self.cls(column_def["schema_code"])

            on_delete_action = "CASCADE" if self.is_required(key) else "SET NULL"
            # on_delete_action = 'NO ACTION'

            txt += (
                """---- {sql_schema_code}.{sql_table_name} foreign key constraint {fk_key_field_name}

ALTER TABLE {sql_schema_code}.{sql_table_name}
    ADD CONSTRAINT fk_{sql_schema_code}_{sql_table_name_short}_{rel_sql_table_name_short}_{fk_key_field_name} FOREIGN KEY ({fk_key_field_name})
    REFERENCES {rel_sql_schema_code}.{rel_sql_table_name}({rel_pk_key_field_name})
    ON UPDATE CASCADE ON DELETE {on_delete_action};

"""
            ).format(
                sql_schema_code=self.sql_schema_code(),
                sql_table_name=self.sql_table_name(),
                sql_table_name_short=self.sql_table_name()[0:5],
                fk_key_field_name=key,
                rel_sql_schema_code=relation.sql_schema_code(),
                rel_sql_table_name=relation.sql_table_name(),
                rel_sql_table_name_short=relation.sql_table_name()[0:5],
                rel_pk_key_field_name=relation.pk_field_name(),
                on_delete_action=on_delete_action,
            )

        return txt

    def short_name(self, x, n=3):
        return x if len(x) <= 2 * n else x[:n] + x[-n:]

    def sql_txt_nomenclature_type_constraint(
        self,
        sql_schema_code,
        sql_table_name,
        nomenclature_field_name,
        nomenclature_type,
    ):

        # eviter les noms trop long pour eviter les doublons en cas de coupure
        constraint_name = "check_nom_type_{sql_schema_code}_{sql_table_name}_{nomenclature_field_name}_{nomenclature_type}".format(
            sql_schema_code=sql_schema_code,
            sql_table_name=sql_table_name,
            nomenclature_field_name=self.short_name(nomenclature_field_name),
            nomenclature_type=self.short_name(nomenclature_type.lower()),
        )

        return f"""
ALTER TABLE {sql_schema_code}.{sql_table_name}
        ADD CONSTRAINT {constraint_name}
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique({nomenclature_field_name},'{nomenclature_type.upper()}'))
        NOT VALID;

"""

    def sql_txt_nomenclature_type_constraints(self):
        """
        créé les containtes sur le type de nomenclatrure
        """

        txt = ""

        for key, column_def in self.columns().items():

            nomenclature_type = column_def.get("nomenclature_type")

            if not nomenclature_type:
                continue

            txt += self.sql_txt_nomenclature_type_constraint(
                self.sql_schema_code(),
                self.sql_table_name(),
                key,
                nomenclature_type,
            )

        if txt:
            txt = """---- nomenclature check type constraints\n""" + txt + "\n"

        return txt
