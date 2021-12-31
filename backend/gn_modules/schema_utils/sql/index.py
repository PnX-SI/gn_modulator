'''
    SchemaSqlIndex
'''


class SchemaSqlIndex():
    '''
        methods pour gerer les index
    '''

    def sql_txt_process_index(self):
        '''
            methode pour gerer les index associés à un schema
        '''

        txt = ''
        for property_key, property_def in self.properties().items():
            txt += self.sql_txt_process_property_index(property_key, property_def)

        if txt:
            txt = '\n-- Indexes\n\n\n' + txt
        return txt

    def sql_txt_process_property_index(self, property_key, property_def):
        '''
            fonction qui cree les trigger associé à un élément d'un schema
        '''

        if not property_def.get('index'):
            return ''

        if property_def['type'] == 'geometry':

            txt = '''CREATE INDEX {sql_schema_name}_{sql_table_name}_{property_key}_idx
    ON {sql_schema_name}.{sql_table_name}
    USING GIST ({property_key});\n'''.format(
                sql_schema_name=self.sql_schema_name(),
                sql_table_name=self.sql_table_name(),
                property_key=property_key
            )

            return txt

        return ''