'''
    SchemaMethods : sqlalchemy models processing
'''

from geonature.utils.env import DB

class SchemaModel():
    '''
        sqlalchemy models processing
    '''

    def model_name(self):
        '''
            returns model_name
            can be 
              - defined in self._schema['$meta']['model_name'] 
              - or retrieved from module_code and schema_name 'T{full_name('pascal_case')}'
        '''

        return self._schema['$meta'].get('model_name', 'T{}'.format(self.full_name('pascal_case')))        

    def Model(self):
        '''
        create and returns schema Model : a class created with type(name, (bases,), dict_model) function
        - name : self.model_name()
        - base :  DB.Model
        - dict_model : contains properties and methods

        TODO store in global variable and create only if missing
        - avoid to create the model twice
        '''

        # dict_model used with type() to list properties and methods for class creation
        dict_model = {
            '__tablename__': self.sql_table_name(),
            '__table_args__': {
                'schema': self.sql_schema_name(),
                'extend_existing': True # TODO remove and storage for class
            }
        }

        # process properties
        for key, value in self.properties(processed_properties_only=True).items():

            # get field_options
            field_options = {}
            field_type = value['type']
            if value.get('primary_key'):
                field_options['primary_key'] = True
            
            # process type
            if field_type == 'integer':
                dict_model[key] = DB.Column(DB.Integer, **field_options)
                pass
            elif field_type == 'string':
                dict_model[key] = DB.Column(DB.Unicode, **field_options)
                pass
            else:
                raise(
                    SchemaProcessedPropertyError(
                    'Property type {} in processed_properties but not managed yet for SQL processing'
                    .format(field_type)
                )
            )

        return type(self.model_name(), (DB.Model,), dict_model)