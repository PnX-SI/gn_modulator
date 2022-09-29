'''
    SchemaMethods : sqlalchemy queries processing
'''

from dataclasses import field
import math

from geonature.utils.env import db

from sqlalchemy import func, select, alias
from sqlalchemy.orm import defer
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

    def insert_row(self, data):
        '''
            insert new row with data
        '''

        if self.pk_field_name() in data and data[self.pk_field_name()] is None:
            data.pop(self.pk_field_name())

        self.validate_data(data)
        m = self.Model()()
        self.unserialize(m, data)
        db.session.add(m)
        db.session.commit()

        return m

    def is_new_data(self, model, data):
        '''
            for update_row
            test if data different from model
        '''

        if model is None and data is not None:
            return True

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

        db.session.flush()
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

    def process_query_columns(self, params, query, order_by):
        '''
            permet d'ajouter de colonnes selon les besoin
            - ownership pour cruved (toujours?)
            - row_number (si dans fields)
        '''

        fields = params.get('fields', [])

        # cruved
        if 'ownership' in fields:
            query = self.add_column_ownership(query)

        # row_number
        if 'row_number' in fields:
            query = query.add_columns(
                func.row_number()
                .over(order_by=order_by)
                .label('row_number')
            )

        return query



    def get_row_number(self, params, value):

        Model = self.Model()
        query = db.session.query(Model)

        params['fields'] = [self.pk_field_name(), 'row_number']

        order_bys, query = self.get_sorters(Model, params.get('sorters', []), query)
        query = self.process_query_columns(params, query, order_bys)
        
        query = self.process_cruved_filter('R', 'MODULE ?? TODO', query)
        query = self.process_filters(Model, params.get('prefilters', []), query)
        query = self.process_filters(Model, params.get('filters', []), query)
 
        subquery = query.subquery()
 
        res = (
            db.session.query(subquery)
            .filter(getattr(subquery.c, self.pk_field_name()) == value)
            .one()
        )
        return res.row_number

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

        model_pk_field = getattr(Model, self.pk_field_name())

        # essayer de ne mettre que les colonnes ???

        # query_fields = []
        # for field in params['fields']:
        #     if field in ['ownership', 'row_number']:
        #         continue
        #     model_attribute, query = self.custom_getattr(Model, field)
        #     query_fields.append(model_attribute)

        # query = db.session.query(*query_fields)
        query = db.session.query(Model)


        # optimisation de la requete pour ne pas appeler tous les champs
        # test
        fields = params.get('fields', [])
        if not self.pk_field_name() in fields:
            fields.append(self.pk_field_name())

        if self.schema_name() in ['modules.module', 'commons.modules']:
            fields.append('type')
            
        defered_fields = [
            defer(getattr(Model, key))
            for key in self.column_properties_keys()
            if key not in fields
        ]

        defered_fields += [
            defer(getattr(Model, key))
            for key in self.column_keys()
            if key not in fields
        ]

        for defered_field in defered_fields:
            try:
                query = query.options(defered_field)
            except:
                pass    
        
        order_bys, query = self.get_sorters(Model, params.get('sorters', []), query)

        # process query columns
        # ajout de colonnes
        # - cruved
        # - row_number
        # - enlever les colonnes non demandées ????
        query = self.process_query_columns(params, query, order_bys)

        # prefilters

        # - CRUVED : process_cruved
        #   - ajout de la colonne ownership
        #   - filtre selon le cruved

        query = self.process_cruved_filter('R', 'MODULE ?? TODO', query)

        query = self.process_filters(Model, params.get('prefilters', []), query)
         
        query_info['total'] = (
            query
                .with_entities(model_pk_field)
                .group_by(model_pk_field)
                .count()
        )

        if params.get('page_size'):
            query_info['last_page'] = math.ceil(query_info['total'] / params.get('page_size'))

        # filters
        query = self.process_filters(Model, params.get('filters', []), query)
        
        query_info['filtered'] = (
            query
                .with_entities(model_pk_field)
                .group_by(model_pk_field)
                .count()
        )

        query = query.order_by(*(tuple(order_bys)))

        if params.get('page_size'):
            query_info['last_page'] = math.ceil(query_info['total'] / params.get('page_size'))

        # page, page_size
        query = self.process_page_size(params.get('page'), params.get('page_size'), params.get('value'), query)

        return query, query_info
