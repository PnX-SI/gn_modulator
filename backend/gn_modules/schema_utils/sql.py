'''
    SchemaMethods : SQL 
    
    SQL text production methods for schema
'''

from .errors import SchemaSqlError, SchemaProcessedPropertyError
from geonature.utils.env import DB

class SchemaSql():

    def sql_create_schema(self, mode='txt'):
        '''
            Create schema sql schema
        '''
        txt = 'CREATE SCHEMA {};'.format(self.sql_schema_name())
        if mode == 'exec':
            DB.engine.execute(txt)
        return txt

    def sql_drop_schema(self, check_if_exists=False, mode='txt'):
        '''
            Drop schema sql schema

            Jamais de drop cascade !!!!!!! 
        '''

        if_exists_txt = 'IF EXISTS ' if check_if_exists else ''

        txt = 'DROP SCHEMA {}{};'.format(if_exists_txt, self.sql_schema_name())
        if mode == 'exec':
            DB.engine.execute(txt)
        return txt

    def sql_create_table(self, mode='txt'):
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
        
        txt+=(
            'CREATE TABLE  {}.{} (\n'
            .format(
                self.sql_schema_name(),
                self.sql_table_name()
            )
        )
        
        # liste des champs
        for key, value in self.properties(processed_properties_only=True).items():
            field_type = value['type']
            if field_type == 'integer':
                txt+='    {} {},\n'.format(key, 'SERIAL NOT NULL' if value.get('primary_key') else 'INTEGER')
            elif field_type == 'string':
                txt+='    {} VARCHAR,\n'.format(key) 
            else:
                raise SchemaProcessedPropertyError(
                    'Property type {} in processed_properties but not managed yet for SQL processing'
                    .format(field_type)
                )
        

        # contraintes

        #  - cle primaire
        pk_field_names = self.pk_field_names()
        if not pk_field_names:
            raise SchemaSqlError('Il n''y a pas de clé primaire définie pour le schema {sql_schema} {sql_table}')

        txt += (
            '    CONSTRAINT pk_{}_{}_{} PRIMARY KEY ({}),\n'
            .format(self.sql_schema_name(), self.sql_table_name(), '_'.join(pk_field_names), ', '.join(pk_field_names))
        )

        # TODO relations et clés étrangères

        # finalisation 
        #  - suppresion de la dernière virgule
        #  - fermeture de la parenthèse
        #  - point virgule final 
        txt = txt[:-2] + '\n)\n;\n' 

        if mode == 'exec':
            DB.engine.execute(txt)
        
        return txt
        

    def sql_drop_table(self, check_if_exists=False, mode='txt'):
        '''
            code sql qui permet de supprimer la table du schema

            - check_if_exists permet d'utiliser DROP TABLE IF EXISTS
        '''
        txt = ''
        
        if_exists_txt = 'IF EXISTS ' if check_if_exists else ''

        txt+='DROP TABLE {}{}.{};'.format(if_exists_txt, self.sql_schema_name(), self.sql_table_name())

        if mode == 'exec':
            DB.engine.execute(txt)

        return txt