'''
    SchemaMethods : sqlalchemy queries processing
'''

from .queries import (
    custom_getattr,
    process_filters,
    process_sorters,
    process_page_size,
    # reset_cache_custom_getattr
)

from .errors import (
    SchemaRepositoryError
)

import math

from geonature.utils.env import DB


class SchemaRepositories():
    '''
        class for sqlalchemy query processing
    '''

    def get_row(self, value, field_name=None, b_get_one=True):
        '''
            return query get one row (Model.<field_name> == value)

            - value
            - field_name:
              - filter by <field_name>==value
              - if field_name is None, use primary key field name

            - value and field name can be arrays, they must be of same size


            DB.session.query(Model).filter(<field_name> == value).one()
        '''

        if not field_name:
            field_name = self.pk_field_name()

        # value et field_name peuvent être des listes
        # pour la suite nous traitons tout comme des listes
        values = value if type(value) is list else [value]
        field_names = field_name if type(field_name) is list else [field_name]

        if len(values) != len(field_names):
            raise SchemaRepositoryError(
                'get_row : les input value et field_name n''ont pas la même taille'
            )

        Model = self.Model()

        query = DB.session.query(Model)

        for index, val in enumerate(values):
            f_name = field_names[index]
            modelValue, query = custom_getattr(Model, f_name, query)
            query = query.filter(modelValue == val)

        if b_get_one:
            return query.one()

        return query

    def insert_row(self, data):
        '''
            insert new row with data
        '''

        self.validate_data(data)
        m = self.Model()()
        self.unserialize(m, data)
        DB.session.add(m)
        DB.session.commit()

        return m

    def is_new_data(self, model, data):
        '''
            for update_row
            test if data different from model
        '''

        for k, v in data.items():
            if type(v) is dict:
                m = getattr(model, k)
                return self.is_new_data(m, v)

            elif type(v) is list:
                print(v)
                return True
                # model_value, _ = custom_getattr(model, k)
                # print(k, v, model_value)
                # raise Exception('list no processed in is_new_data just do it!!!!!!')
            else:
                model_value, _ = custom_getattr(model, k)
                if model_value != v:
                    return True
        return False

    def update_row(self, value, data, field_name=None):
        '''
            update row (Model.<field_name> == value) with data

            # TODO deserialiser
        '''
        self.validate_data(data)
        m = self.get_row(value, field_name=field_name)
        if not self.is_new_data(m, data):
            return m, False
        print('is new')
        self.unserialize(m, data)
        DB.session.commit()
        return m, True

    def delete_row(self, id, field_name=None):
        '''
            delete row (Model.<field_name> == value)
        '''
        m = self.get_row(id, field_name=field_name, get_one=False)
        m.delete()
        DB.session.commit()
        return m

    def get_list(self, params={}):
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

        # remise à zero du cache
        # reset_cache_custom_getattr()

        query_info = {
            'page': params.get('page', None),
            'size': params.get('size', None)
        }

        # init query
        Model = self.Model()
        query = DB.session.query(Model)

        # TODO distinguer filter et filter search
        query_info['total'] = query.count()

        if params.get('size'):
            query_info['last_page'] = math.ceil(query_info['total'] / params.get('size'))

        # filters
        query = process_filters(Model, params.get('filters', []), query)

        # TODO distinguer filter et filter search
        query_info['filtered'] = query.count()

        if params.get('size'):
            query_info['last_page'] = math.ceil(query_info['filtered'] / params.get('size'))

        # CRUVED ??? TODO comment faire
        # query = process_cruved(Model, query)

        # sorters
        query = process_sorters(Model, params.get('sorters', []), query)

        # page, size
        query = process_page_size(params.get('page'), params.get('size'), query)

        return query, query_info
