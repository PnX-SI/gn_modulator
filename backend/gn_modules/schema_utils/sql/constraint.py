'''
    SchemaSqlConstraints
'''

from ..errors import (
    SchemaSqlError
)


class SchemaSqlConstraint():
    '''
        methods pour gerer les contraintes
    '''

    def sql_txt_primary_key_constraints(self):
        '''
            créé la containte de clé(s) primaire(s)
        '''

        #  - clés primaires

        pk_field_names = self.pk_field_names()

        if not pk_field_names:
            raise SchemaSqlError('Il n''y a pas de clé primaire définie pour le schema {sql_schema} {sql_table}')

        return ("""---- {sql_schema_name}.{sql_table_name} primary key constraint

ALTER TABLE {sql_schema_name}.{sql_table_name}
    ADD CONSTRAINT pk_{sql_schema_name}_{sql_table_name}_{pk_keys_dash} PRIMARY KEY ({pk_keys_commas});

""".format(
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name(),
                pk_keys_dash='_'.join(pk_field_names),
                pk_keys_commas=', '.join(pk_field_names),
                )
                )

    def sql_txt_foreign_key_constraints(self):
        '''
            créé les containtes de clés étrangères
        '''
        txt = ""

        for key, column_def in self.columns().items():

            foreign_key = self.get_foreign_key(column_def)

            if not foreign_key:
                continue

            relation_name, fk_field_name = self.parse_foreign_key(foreign_key)
            relation = self.cls()(relation_name)

            txt += (
                """---- {sql_schema_name}.{sql_table_name} foreign key constraint {fk_key_field_name}

ALTER TABLE {sql_schema_name}.{sql_table_name}
    ADD CONSTRAINT fk_{sql_schema_name}_{sql_table_name_short}_{rel_sql_table_name_short}_{fk_key_field_name} FOREIGN KEY ({fk_key_field_name})
    REFERENCES {rel_sql_schema_name}.{rel_sql_table_name}({rel_pk_key_field_name})
    ON UPDATE CASCADE ON DELETE NO ACTION;

""").format(
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name(),
                sql_table_name_short=self.sql_table_name()[0:5],
                fk_key_field_name=key,
                rel_sql_schema_name=relation.sql_schema_name(),
                rel_sql_table_name=relation.sql_table_name(),
                rel_sql_table_name_short=relation.sql_table_name()[0:5],
                rel_pk_key_field_name=fk_field_name
            )

        return txt

    def sql_txt_nomenclature_type_constraints(self):
        '''
            créé les containtes sur le type de nomenclatrure
        '''

        txt = ""

        for key, column_def in self.columns().items():

            nomenclature_type = column_def.get('nomenclature_type')

            if not nomenclature_type:
                continue

            txt += (
                """
ALTER TABLE {sql_schema_name}.{sql_table_name}
        ADD CONSTRAINT check_nom_type_{sql_schema_name}_{sql_table_name}_{nomenclature_type}
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique({nomenclature_field_name},'{NOMENCLATURE_TYPE}'))
        NOT VALID;
""").format(
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name(),
                nomenclature_field_name=key,
                NOMENCLATURE_TYPE=nomenclature_type.upper(),
                nomenclature_type=nomenclature_type.lower(),
            )

        if txt:
            txt = """---- nomenclature check type constraints\n""" + txt + '\n'

        return txt
