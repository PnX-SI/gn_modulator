'''
    SchemaMethods : SQL 
    
    SQL text production methods for schema
'''

from sqlalchemy import select, exists, and_, text, inspect

from geonature.utils.env import DB

from .errors import (
    SchemaSqlError,
    SchemaProcessedPropertyError,
    SchemaUnautorizedSqlError
)



class SchemaSql():

    def sql_schema_name(self):
        '''
            returns sql_schema_name from self._schema['$meta']
            can be 
              - defined in self._schema['$meta']['sql_schema_name'] 
              - or retrieved from group_name : 'm_{group_name}' 
        '''
        return self._schema['$meta'].get('sql_schema_name', 'm_{}'.format(self.group_name()))

    def sql_table_name(self):
        '''
            !! can be confused with object_name
            returns sql_table_name from self._schema['$meta']
            can be 
              - defined in self._schema['$meta']['sql_table_name'] 
              - or retrieved from group_name : 't_{object_name}' 
        '''
        return self._schema['$meta'].get('sql_table_name', 't_{}s'.format(self.object_name()))

    def sql_schema_dot_table(self):
        return '{}.{}'.format(self.sql_schema_name(), self.sql_table_name())

    def sql_schema_exists(self):
        '''
            check if sql schema exists
        '''
        return self.sql_schema_name() in inspect(DB.engine).get_schema_names()

    def sql_table_exists(self):
        '''
            check if sql table exists
        '''
        return self.sql_table_name() in inspect(DB.engine).get_table_names(self.sql_schema_name())

    def sql_txt_create_schema(self):
        '''
            Create schema sql schema
        '''
        txt = 'CREATE SCHEMA {};'.format(self.sql_schema_name())
        return txt

    def sql_txt_drop_schema(self):
        '''
            Drop schema sql schema

            Jamais de drop cascade !!!!!!! 
        '''

        txt = 'DROP SCHEMA {}{};'.format(self.sql_schema_name())
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
        
        txt+= ( 
"""-- sql code for jsonschema : {schema_id}


---- table {sql_schema_name}.{sql_table_name} creation

CREATE TABLE  {sql_schema_name}.{sql_table_name} (
"""
            .format(
                schema_id=self.full_name(),
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name()
            )
        )

        # liste des champs
        for key, value in self.properties(processed_properties_only=True).items():
            field_type = value['type']
            if field_type == 'integer':
                txt+='    {} {},\n'.format(key, 'SERIAL NOT NULL' if value.get('primary_key') else 'INTEGER')
            elif field_type =='text':
                txt+='    {} VARCHAR,\n'.format(key)
            elif field_type == 'number':
                txt+='    {} FLOAT,\n'.format(key)
            else:
                raise SchemaProcessedPropertyError(
                    'Property type {} in processed_properties but not managed yet for SQL processing'
                    .format(field_type)
                )


    
        # TODO relations et clés étrangères

        # finalisation 
        #  - suppresion de la dernière virgule
        #  - fermeture de la parenthèse
        #  - point virgule final 
        txt = txt[:-2] + '\n);\n' 

    # # contraintes

        #  - cle primaire
        pk_field_names = self.pk_field_names()
        if not pk_field_names:
            raise SchemaSqlError('Il n''y a pas de clé primaire définie pour le schema {sql_schema} {sql_table}')

        txt += (
            """

---- constraints : 

------ primary key constraint

ALTER TABLE {sql_schema_name}.{sql_table_name}
    ADD CONSTRAINT pk_{sql_schema_name}_{sql_table_name}_{pk_keys_dash} PRIMARY KEY ({pk_keys_commas});
"""
            .format(
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name(),
                pk_keys_dash='_'.join(pk_field_names),
                pk_keys_commas=', '.join(pk_field_names),
            )
        )


        txt += """
------ foreign keys constraints

"""
        # Clé étrangère
        for key, value in self.properties(processed_properties_only=True).items():

            if not value.get('foreign_key'):
                continue

            relation_reference = value.get('foreign_key')
            sm_relation = self.__class__().load_from_reference(relation_reference)

            txt += (
"""ALTER TABLE {sql_schema_name}.{sql_table_name}
    ADD CONSTRAINT fk_{sql_schema_name}_{sql_table_name}_{rel_sql_table_name}_{fk_key_field_name} FOREIGN KEY ({fk_key_field_name})
    REFERENCES {rel_sql_schema_name}.{rel_sql_table_name}({rel_pk_key_field_name})
    ON UPDATE CASCADE ON DELETE NO ACTION;
"""
            ).format(
                    sql_schema_name=self.sql_schema_name(),
                    sql_table_name=self.sql_table_name(),
                    fk_key_field_name=key,
                    rel_sql_schema_name=sm_relation.sql_schema_name(),
                    rel_sql_table_name=sm_relation.sql_table_name(),
                    rel_pk_key_field_name=sm_relation.pk_field_name()
            )

#         for key, value in self.relationships().items():

#             sm_rel = self.__class__().load_from_reference(value['$ref'])

#             if value.get('fk'):
#                 txt += (
# """ALTER TABLE {sql_schema_name}.{sql_table_name}
#     ADD CONSTRAINT fk_{sql_schema_name}_{sql_table_name}_{rel_sql_table_name}_{fk_key_field_name} FOREIGN KEY ({fk_key_field_name})
#     REFERENCES {rel_sql_schema_name}.{rel_sql_table_name}({rel_pk_key_field_name})
#     ON UPDATE CASCADE ON DELETE NO ACTION;
# """
#                 ).format(
#                     sql_schema_name=self.sql_schema_name(),
#                     sql_table_name=self.sql_table_name(),
#                     fk_key_field_name=value['fk'],
#                     rel_sql_schema_name=sm_rel.sql_schema_name(),
#                     rel_sql_table_name=sm_rel.sql_table_name(),
#                     rel_pk_key_field_name=sm_rel.pk_field_name()
#                 )

        return txt

    def sql_processing(self):
        ''' 
            Variable meta
                - pour authoriser l'execution de script sql pour le schema
                - par defaut à False
        '''
        return self._schema["$meta"].get("sql_processing", False)

    def sql_exec_txt(self, txt):
        '''
            - exec txt as sql
            - remove empty or comments or empty lines and exec sql
              - DB.engine.execute doesn't process sql text with comments
        '''

        if not self.sql_processing():
            raise SchemaUnautorizedSqlError(
                "L'exécution de commandes sql n'est pas autorisé pour le schema {} {}"
                .format(self.group_name(), self.object_name())
            )

        txt_no_comment = '\n' .join(
            filter(
                lambda l : (l and not l.strip().startswith('--')),
                txt.split('\n')
            )
        )
        return DB.engine.execute(txt_no_comment)

    def sql_txt_drop_table(self):
        '''
            code sql qui permet de supprimer la table du schema
        '''
        txt = ''
        
        txt+='DROP TABLE {}.{};'.format(self.sql_schema_name(), self.sql_table_name())

        return txt