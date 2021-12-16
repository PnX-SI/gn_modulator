'''
    SchemaMethods : sqlalchemy queries processing
'''

import math

from geonature.utils.env import DB

from sqlalchemy import cast, orm, and_, or_, not_, func, select
from sqlalchemy.sql.selectable import subquery

from ..errors import (
    SchemaRepositoryError
)


class SchemaRepositoriesBase():
    '''
        class for sqlalchemy query processing
    '''

    def get_row(self, value, field_name=None, b_get_one=True, info_role=None):
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
        values = value if isinstance(value, list) else [value]
        field_names = field_name if isinstance(field_name, list) else [field_name]

        if len(values) != len(field_names):
            raise SchemaRepositoryError(
                'get_row : les input value et field_name n''ont pas la même taille'
            )

        Model = self.Model()

        query = DB.session.query(Model)

        for index, val in enumerate(values):
            f_name = field_names[index]
            modelValue, query = self.custom_getattr(Model, f_name, query)
            query = query.filter(modelValue == val)

        if b_get_one:
            return query.one()

        return query

    def insert_row(self, data, info_role=None):
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

        if isinstance(data, dict) and not isinstance(model, dict):
            for key, data_value in data.items():
                m = self.serialize(model, fields=[key])[key]
                if self.is_new_data(m, data_value):
                    return True
            return False

        if isinstance(data, list):
            print('list', model, data)

            # test list
            if not isinstance(model, list):
                # raise error ?
                return False

            # test taille
            if len(data) != len(model):
                return False

            # test s'il y a une correspondance pour chaque element
            for data_elem in data:
                is_new_data = True
                for model_elem in model:
                    if not is_new_data:
                        break
                    is_new_data = is_new_data and self.is_new_data(model_elem, data_elem)

                if is_new_data:
                    return True

            return False

        # element à element
        # pour les uuid la comparaison directe donne non egal en cas d'égalité
        # (pourquoi??) d'ou transformation en string pour la comparaison
        if not (model == data or str(model) == str(data)):
            print('elem diff', data, model)
            return True

        return False

    def update_row(self, value, data, field_name=None, info_role=None):
        '''
            update row (Model.<field_name> == value) with data

            # TODO deserialiser
        '''
        self.validate_data(data)
        m = self.get_row(value, field_name=field_name)
        if not self.is_new_data(m, data):
            print('not new')
            return m, False
        self.unserialize(m, data)
        DB.session.commit()
        return m, True

    def delete_row(self, value, field_name=None, info_role=None):
        '''
            delete row (Model.<field_name> == value)
        '''
        m = self.get_row(value, field_name=field_name, b_get_one=False)
        m.delete()
        DB.session.commit()
        return m

    def get_row_number(self, params, value, info_role=None):

        Model = self.Model()
        query = DB.session.query(Model.id_pf)
        query = query.add_columns(func.row_number().over(order_by=self.get_sorters(Model, params.get('sorters', []), query)))

        # pre_filters
        query = self.process_cruved(info_role, 'R', Model, query)

        # filters
        query = self.process_filters(Model, params.get('filters', []), query)

        # sorters ?? redondant avec row_number order_by ?
        query = self.process_sorters(Model, params.get('sorters', []), query)

        # query row number
        field_name = self.pk_field_name()
        print(value, field_name)
        sub_query = query.subquery()
        res = DB.session.query(sub_query).filter(getattr(sub_query.c, field_name) == value).one()

        return res[1]

    def get_page_number(self, params, value, info_role=None):

        if not params.get('size') and value:
            return

        row_number = self.get_row_number(params, value, info_role)

        return {
            'row_number': row_number,
            'page': math.ceil(row_number / params.get('size'))
        }

    def get_list(self, params, info_role=None):
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


        query_info = {
            'page': params.get('page', None),
            'size': params.get('size', None)
        }

        # if params['value']:
        #     row_number = self.get_row_number(params, params['value'], info_role)
        #     query_info['row_number'] = row_number
        #     print('row number', row_number, 'id_pf', params['value'])


        # init query
        Model = self.Model()
        query = DB.session.query(Model)

        # CRUVED ??? TODO
        query = self.process_cruved(info_role, 'R', Model, query)

        # pre filters

        # row number

        query = self.process_sorters(Model, params.get('sorters', []), query)

        # TODO distinguer filter et pre_filter search
        query_info['total'] = query.count()

        if params.get('size'):
            query_info['last_page'] = math.ceil(query_info['total'] / params.get('size'))

        # filters
        query = self.process_filters(Model, params.get('filters', []), query)

        # TODO distinguer filter et filter search
        query_info['filtered'] = query.count()

        if params.get('size'):
            query_info['last_page'] = math.ceil(query_info['filtered'] / params.get('size'))
            # if query_info.get('row_number'):
            #     query_info['value_page'] = math.ceil(query_info['row_number'] / params.get('size'))

        # sorters

        query = self.process_sorters(Model, params.get('sorters', []), query)

        # if params.get('value'):
        #     query_info['row_number'] = self.get_row_number_from_value(params.get('value'), query)

        # page, size
        query = self.process_page_size(params.get('page'), params.get('size'), params.get('value'), query)

        return query, query_info
