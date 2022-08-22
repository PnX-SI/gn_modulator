'''
    SchemaMethods : sqlalchemy queries processing
'''

import math

from geonature.utils.env import db
from pyrsistent import v

from sqlalchemy import cast, orm, and_, or_, not_, func, select

from .. import errors


class SchemaRepositoriesBase():
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


            db.session.query(Model).filter(<field_name> == value).one()
        '''

        if not field_name:
            field_name = self.pk_field_name()

        # value et field_name peuvent être des listes
        # pour la suite nous traitons tout comme des listes
        values = value if isinstance(value, list) else [value]
        field_names = field_name if isinstance(field_name, list) else [field_name]

        if len(values) != len(field_names):
            raise errors.SchemaRepositoryError(
                'get_row : les input value et field_name n''ont pas la même taille'
            )

        Model = self.Model()
        self.set_cruved()

        query = db.session.query(Model)

        for index, val in enumerate(values):
            f_name = field_names[index]
            # patch si la valeur est une chaine de caractère ??
            # if self.column(f_name)['type'] == "integer" and val is not None:
                # val = int(val)

            modelValue, query = self.custom_getattr(Model, f_name, query)
            query = query.filter(modelValue == val)

        if b_get_one:
            return query.one()

        return query

    def insert_row(self, data, commit=True):
        '''
            insert new row with data
        '''

        if self.pk_field_name() in data and data[self.pk_field_name()] is None:
            data.pop(self.pk_field_name())

        self.validate_data(data)
        m = self.Model()()
        self.unserialize(m, data)
        db.session.add(m)
        if commit:
            db.session.commit()

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
            # test list
            if not isinstance(model, list):
                # raise error ?
                raise Exception('error list')

            # test taille
            if len(data) != len(model):
                return True

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
        if isinstance(data, dict):
            model = {
                key: model[key]
                for key in data
                if key in model
            }
        if not (model == data or str(model) == str(data)):
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

        self.unserialize(m, data)
        db.session.commit()

        return m, True

    def delete_row(self, value, field_name=None):
        '''
            delete row (Model.<field_name> == value)
        '''
        m = self.get_row(value, field_name=field_name, b_get_one=False)
        m.delete()
        db.session.commit()
        return m

    def get_row_number(self, params, value):
        """
            todo UN SUEL
        """
        Model = self.Model()
        self.set_cruved()

        query = db.session.query(Model)

        # pre_filters
        query = self.process_cruved('R', Model, query)
        query = self.process_filters(Model, params.get('prefilters', []), query)


        # filters
        query = self.process_filters(Model, params.get('filters', []), query)

        # sorters ?? redondant avec row_number order_by ?
        query = self.process_sorters(Model, params.get('sorters', []), query)

        # query row number
        order_by, query = self.get_sorters(Model, params.get('sorters', []), query)
        query = query.add_columns(func.row_number().over(order_by=order_by))
        sub_query = query.subquery()
        field_name = self.pk_field_name()
        res = db.session.query(sub_query).filter(getattr(sub_query.c, field_name) == value).one()

        return res[-1]

    def get_page_number(self, params, value):

        if not params.get('page_size') and value:
            return

        row_number = self.get_row_number(params, value)

        return {
            'row_number': row_number,
            'page': math.ceil(row_number / params.get('page_size'))
        }

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
            - page_size ( LIMIT )
            - page ( OFFSET(page_size, page) )
        '''



        query_info = {
            'page': params.get('page', None),
            'page_size': params.get('page_size', None)
        }

        # init query
        Model = self.Model()
        self.set_cruved()
        query = db.session.query(Model)

        query = self.process_sorters(Model, params.get('sorters', []), query)

        # CRUVED et prefilters
        query = self.process_cruved('R', Model, query)
        query = self.process_filters(Model, params.get('prefilters', []), query)

        # TODO distinguer filter et pre_filter search
        query_info['total'] = query.count()

        if params.get('page_size'):
            query_info['last_page'] = math.ceil(query_info['total'] / params.get('page_size'))

        # filters
        query = self.process_filters(Model, params.get('filters', []), query)

        # TODO distinguer filter et filter search

        query_info['filtered'] = query.count()

        if query_info['filtered'] > query_info['total']:
            raise Exception('Pb filtered {} > total {} pour get_list {}'.format(
                query_info['filtered'],
                query_info['total'],
                self.schema_name()
            ))

        if params.get('page_size'):
            query_info['last_page'] = math.ceil(query_info['filtered'] / params.get('page_size'))

        # page, page_size
        query = self.process_page_size(params.get('page'), params.get('page_size'), params.get('value'), query)

        return query, query_info
