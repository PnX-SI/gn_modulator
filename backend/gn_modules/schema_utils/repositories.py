'''
    SchemaMethods : sqlalchemy queries processing
'''

from .queries import (
    process_filters,
    process_sorters,
    process_page_size
)

from geonature.utils.env import DB

class SchemaRepositories():
    '''
        class for sqlalchemy query processing
    '''

    def get_row(self, value, field_name=None):
        '''
            return query get one row (Model.<field_name> == value)

            if field_name is None, filter by primary key field name            
            DB.session.query(Model).filter(<field_name> == value).one()
        '''
        if not field_name:
            field_name = self.pk_field_name()
        Model = self.Model()
        return (
            DB.session.query(Model)
            .filter(getattr(Model, field_name) == value)
            .one()    
        )

    def insert_row(self, data):
        '''
            insert new row with data
        '''
        self.validate_data(data)
        Model = self.Model()
        m = Model(**data)
        DB.session.add(m)
        self.unserialize(m, data)
        DB.session.commit()
        return m

    def update_row(self, value, data, field_name=None):
        '''
            update row (Model.<field_name> == value) with data

            # TODO deserialiser
        '''
        self.validate_data(data)
        m = self.get_row(value, field_name)
        self.unserialize(m, data)
        DB.session.commit()
        return m

    def delete_row(self, id, field_name=None):
        '''
            delete row (Model.<field_name> == value)
        '''
        m = self.get_row(id, field_name)
        m.delete()
        DB.session.commit()
        return m

    def get_list(self, params = {}):
        '''
            process request for list of rows
            - params : dict
            - filters ( WHERE ) : [ ...
                {'field': <f_field>, 'type': <f_type>, 'value', <f_value>}
                ... ],
            - sorters ( ORDER BY ): [ ...
                {'field': <s_field>, 'dir': <s_dir>}
                ... ],
                TODO traiter 
            - size ( LIMIT )
            - page ( OFFSET(size, page) )
        '''

        # init query
        Model = self.Model()
        query = DB.session.query(Model)

        # filters
        query = process_filters(Model, params.get('filters', []), query)

        # sorters
        query = process_sorters(Model, params.get('sorters', []), query)

        # page, size
        query = process_page_size(params.get('page'), params.get('size'), query)

        return query

