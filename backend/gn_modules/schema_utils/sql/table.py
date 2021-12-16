'''
    sql table
'''


class SchemaSqlTable():
    '''
        sql table and correlation table
    '''

    def cor_first(self, relation_def):
        return self.cls()(relation_def['first'])

    def cor_second(self, relation_def):
        return (
            self.cls()(relation_def['rel']) if relation_def['first'] == self.schema_name()
            else self
        )

    def cor_schema_name(self, relation_def):
        first = self.cor_first(relation_def)
        return relation_def.get('cor_schema_name', first.sql_schema_name())

    def cor_table_name(self, relation_def):
        first = self.cor_first(relation_def)
        second = self.cor_second(relation_def)
        cor_table_name = relation_def.get('cor_table_name', 'cor_{}_{}'.format(first.object_name(), second.object_name()))
        if relation_def.get('cor_suffix'):
            cor_table_name += '_{}'.format(relation_def.get('cor_suffix'))
        return cor_table_name

    def cor_schema_dot_table(self, relation_def):
        return '{}.{}'.format(self.cor_schema_name(relation_def), self.cor_table_name(relation_def))
        pass

    def sql_txt_process_correlations(self):
        '''
            fonction qui cree les table de correlation associée
        '''

        txt = ''
        for key, relation_def in self.relationships().items():
            txt += self.sql_txt_process_correlation(relation_def)

        return txt

    def sql_txt_process_correlation(self, relation_def):
        '''
            fonction qui cree les table de correlation associée
        '''
        txt = ''

        if not self.relation_type(relation_def) == 'n-n':
            return txt

        local_key = relation_def['local_key']
        local_key_type = self.get_sql_type(self.column(local_key), cor_table=True)
        local_table_name = self.sql_table_name()
        local_schema_name = self.sql_schema_name()

        relation = self.cls()(relation_def['rel'])
        foreign_key = relation_def['foreign_key']
        foreign_key_type = relation.get_sql_type(relation.column(foreign_key), cor_table=True)
        foreign_table_name = relation.sql_table_name()
        foreign_schema_name = relation.sql_schema_name()

        cor_schema_name = self.cor_schema_name(relation_def)
        cor_table_name = self.cor_table_name(relation_def)
        cor_schema_dot_table = self.cor_schema_dot_table(relation_def)

        txt_args = {
            'cor_schema_name': cor_schema_name,
            'cor_table_name': cor_table_name,
            'cor_schema_dot_table': cor_schema_dot_table,

            'local_key': local_key,
            'local_key_type': local_key_type,
            'local_schema_name': local_schema_name,
            'local_table_name': local_table_name,

            'foreign_key': foreign_key,
            'foreign_key_type': foreign_key_type,
            'foreign_schema_name': foreign_schema_name,
            'foreign_table_name': foreign_table_name,
        }

        txt += (
            """-- cor {cor_schema_dot_table}

CREATE TABLE IF NOT EXISTS {cor_schema_dot_table} (
    {local_key} {local_key_type} NOT NULL,
    {foreign_key} {foreign_key_type} NOT NULL
);


---- {cor_schema_dot_table} primary keys contraints

ALTER TABLE {cor_schema_dot_table}
    ADD CONSTRAINT pk_{cor_schema_name}_{cor_table_name}_{local_key}_{foreign_key} PRIMARY KEY ({local_key}, {foreign_key});

---- {cor_schema_dot_table} foreign keys contraints

ALTER TABLE {cor_schema_dot_table}
    ADD CONSTRAINT fk_{cor_schema_name}_{cor_table_name}_{local_key} FOREIGN KEY ({local_key})
    REFERENCES {local_schema_name}.{local_table_name} ({local_key})
    ON UPDATE CASCADE ON DELETE NO ACTION;

ALTER TABLE {cor_schema_dot_table}
    ADD CONSTRAINT fk_{cor_schema_name}_{cor_table_name}_{foreign_key} FOREIGN KEY ({foreign_key})
    REFERENCES {foreign_schema_name}.{foreign_table_name} ({foreign_key})
    ON UPDATE CASCADE ON DELETE NO ACTION;
"""
            .format(**txt_args)
        )

        return txt

    def sql_txt_create_table(self):
        '''
            fonction qui produit le texte sql pour la creation d'une table

            types :
                - integer -> INTEGER ou SERIAL
                - string -> VARCHAR

            contraintes :
                - pk_field_name

            TODO
            - fk ?? etape 2
        '''

        txt = ''

        txt = (
            """---- table {sql_schema_name}.{sql_table_name}

CREATE TABLE {sql_schema_name}.{sql_table_name} (""".format(
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name()
            )
        )

        # liste des champs
        for key, column_def in self.columns().items():
            sql_type = self.get_sql_type(column_def)
            txt += '\n    {} {},'.format(key, sql_type)

        # TODO relations et clés étrangères

        # finalisation
        #  - suppresion de la dernière virgule
        #  - fermeture de la parenthèse
        #  - point virgule final
        txt = txt[:-1] + '\n);\n\n'

        return txt
