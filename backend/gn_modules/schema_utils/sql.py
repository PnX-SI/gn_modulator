'''
    SchemaMethods : SQL

    SQL text production methods for schema
'''

from sqlalchemy import inspect

from geonature.utils.env import DB

from .errors import (
    SchemaSqlError,
    SchemaProcessedPropertyError,
    SchemaUnautorizedSqlError
)
class SchemaSql():

    def get_sql_type(self, column_def, cor_table=False):
        field_type = column_def.get('type')

        sql_type = self.cls().c_get_type(field_type, "definition", 'sql')['type']

        if column_def.get('primary_key') and not cor_table:
            sql_type = 'SERIAL NOT NULL'

        if field_type == 'geometry':
            sql_type = 'GEOMETRY({}, {})'.format(
                column_def.get('geometry_type', 'GEOMETRY').upper(),
                column_def['srid']
            )

        if not sql_type:
            raise SchemaProcessedPropertyError(
                'Property type {} in processed_properties but not managed yet for SQL processing'
                .format(field_type)
            )

        return sql_type

    def sql_schema_name(self):
        '''
            from meta.sql_schema_name or id
        '''
        return self.meta('sql_schema_name', 'm_{}'.format(self.id().split('/')[-2]))

    def sql_table_name(self):
        '''
            from meta.sql_table_name or id
        '''
        return self.meta('sql_table_name', 't_{}s'.format(self.id().split('/')[-1]))

    def schema_dot_table(self):
        return '{}.{}'.format(self.sql_schema_name(), self.sql_table_name())

    @classmethod
    def c_get_schema_name_from_schema_dot_table(cls, schema_dot_table):
        for schema_name in cls.schema_names('schemas'):

            schema = cls.load_json_file_from_name(schema_name)
            sql_schema_name = schema.get('$meta', {}).get('sql_schema_name')
            sql_table_name = schema.get('$meta', {}).get('sql_table_name')

            if '{}.{}'.format(sql_schema_name, sql_table_name) == schema_dot_table:
                return schema_name

    @classmethod
    def c_sql_schema_dot_table_exists(cls, sql_schema_dot_table):
        sql_schema_name = sql_schema_dot_table.split('.')[0]
        sql_table_name = sql_schema_dot_table.split('.')[1]
        return cls.c_sql_table_exists(sql_schema_name, sql_table_name)


    @classmethod
    def c_sql_table_exists(cls, sql_schema_name, sql_table_name):
        return sql_table_name in inspect(DB.engine).get_table_names(sql_schema_name)

    @classmethod
    def c_sql_schema_exists(cls, sql_schema_name):
        return sql_schema_name in inspect(DB.engine).get_schema_names()

    def sql_schema_exists(self):
        '''
            check if sql schema exists
        '''
        return self.cls().c_sql_schema_exists(self.sql_schema_name())

    def sql_table_exists(self):
        '''
            check if sql table exists
        '''
        return self.cls().c_sql_table_exists(self.sql_schema_name(), self.sql_table_name())

    def sql_txt_create_schema(self):
        '''
            Create schema sql schema
        '''
        txt = 'CREATE SCHEMA  IF NOT EXISTS {};'.format(self.sql_schema_name())
        return txt

    def sql_txt_drop_schema(self):
        '''
            Drop schema sql schema

            Jamais de drop cascade !!!!!!!
        '''

        txt = 'DROP SCHEMA {};'.format(self.sql_schema_name())
        return txt

    def sql_txt_primary_key_constraints(self):
        '''
            créé la containte de clé(s) primaire(s)
        '''

        #  - clés primaires

        pk_field_names = self.pk_field_names()

        if not pk_field_names:
            raise SchemaSqlError('Il n''y a pas de clé primaire définie pour le schema {sql_schema} {sql_table}')

        return ("""---- {sql_schema_name}.{sql_table_name} primary key constraint
ALTER TABLE {sql_schema_name}.{sql_table_name} DROP CONSTRAINT IF EXISTS pk_{sql_schema_name}_{sql_table_name}_{pk_keys_dash};
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
                """---- {sql_schema_name}.{sql_table_name} foreign key constraint
ALTER TABLE {sql_schema_name}.{sql_table_name} DROP CONSTRAINT IF EXISTS fk_{sql_schema_name}_{sql_table_name_short}_{rel_sql_table_name_short}_{fk_key_field_name};
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
ALTER TABLE {sql_schema_name}.{sql_table_name} DROP CONSTRAINT IF EXISTS check_nom_type_{sql_schema_name}_{sql_table_name}_{nomenclature_type};
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
            txt = """\n---- nomenclature check type constraints\n""" + txt

        return txt

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

CREATE TABLE  IF NOT EXISTS {cor_schema_dot_table} (
    {local_key} {local_key_type} NOT NULL,
    {foreign_key} {foreign_key_type} NOT NULL
);

-- {cor_schema_dot_table} foreign keys contraints
ALTER TABLE {cor_schema_dot_table} DROP CONSTRAINT IF EXISTS fk_{cor_schema_name}_{cor_table_name}_{local_key};
ALTER TABLE {cor_schema_dot_table}
    ADD CONSTRAINT fk_{cor_schema_name}_{cor_table_name}_{local_key} FOREIGN KEY ({local_key})
    REFERENCES {local_schema_name}.{local_table_name} ({local_key})
    ON UPDATE CASCADE ON DELETE NO ACTION;

ALTER TABLE {cor_schema_dot_table} DROP CONSTRAINT IF EXISTS fk_{cor_schema_name}_{cor_table_name}_{foreign_key};
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

CREATE TABLE IF NOT EXISTS {sql_schema_name}.{sql_table_name} (""".format(
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
        txt = txt[:-1] + '\n);\n'

        return txt



    def sql_processing(self):
        '''
            Variable meta
                - pour authoriser l'execution de script sql pour le schema
                - par defaut à False
        '''
        return self.meta("sql_processing", False)

    @classmethod
    def c_sql_exec_txt(cls, txt):
        '''
            - exec txt as sql
            - remove empty or comments or empty lines and exec sql
              - DB.engine.execute doesn't process sql text with comments
        '''

        # if not self.sql_processing():
        #     raise SchemaUnautorizedSqlError(
        #         "L'exécution de commandes sql n'est pas autorisé pour le schema {}"
        #         .format(self.schema_name())
        #     )

        txt_no_comment = '\n' .join(
            filter(
                lambda l: (l and not l.strip().startswith('--')),
                txt.split('\n')
            )
        )
        return DB.engine.execute(txt_no_comment)

    def sql_txt_drop_table(self):
        '''
            code sql qui permet de supprimer la table du schema
        '''
        txt = ''

        txt += 'DROP TABLE {}.{};'.format(self.sql_schema_name(), self.sql_table_name())

        return txt

    def dependencies(self, exclude_deps=[]):
        deps = [self.schema_name()]
        for key, relation_def in self.relationships().items():
            rel = relation_def['rel']

            if rel in deps + exclude_deps:
                continue

            deps.append(rel)
            deps += self.cls()(relation_def['rel']).dependencies(exclude_deps=deps + exclude_deps)

        if self.schema_name() in deps:
            deps.remove(self.schema_name())

        return list(dict.fromkeys(deps))

    def sql_txt_process(self):
        '''
            process all sql for a schema
        '''

        if not self.sql_processing():
            return ''

        processed_schema_names = []
        for name in self.dependencies():
            sm = self.cls()(name)
            if sm.sql_processing():  # and not sm.sql_table_exists():
                processed_schema_names.append(name)

        txt = "-- process schema : {}\n".format(self.schema_name())
        if processed_schema_names:
            txt += "--\n-- and dependancies : {}\n".format(', '.join(processed_schema_names))
        txt += '\n\n'

        processed_schema_names.insert(0, self.schema_name())

        # schemas
        sql_schema_names = []
        for name in processed_schema_names:
            sm = self.cls()(name)
            if sm.sql_schema_name() not in sql_schema_names: # and not sm.sql_schema_exists():
                sql_schema_names.append(sm.sql_schema_name())

        for sql_schema_name in sql_schema_names:
            txt += '---- sql schema {sql_schema_name}\n\nCREATE SCHEMA IF NOT EXISTS {sql_schema_name};\n\n'.format(sql_schema_name=sql_schema_name)

        # actions
        for action in [
            'sql_txt_create_table',
            'sql_txt_primary_key_constraints',
            'sql_txt_foreign_key_constraints',
            'sql_txt_nomenclature_type_constraints',
            'sql_txt_process_correlations'
        ]:
            for name in processed_schema_names:
                sm = self.cls()(name)
                txt_action = getattr(sm, action)()
                if txt_action:
                    txt += '{}\n'.format(txt_action)

        return txt
