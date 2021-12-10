from sqlalchemy import cast, orm, and_, or_, not_, func, select
from geonature.utils.env import DB

cache_custom_getattr = {}

class SchemaRepositoriesUtil():
    '''
        custom getattr: retrouver les attribut d'un modele ou des relations du modèles
    '''
    __abstract__ = True

    def custom_getattr(self, Model, field_name, query=None):
        '''
            getattr pour un modèle, étendu pour pouvoir traiter les 'rel.field_name'

            on utilise des lias pour pouvoir gérer les cas plus compliqués

            exemple:

                on a deux relations de type nomenclature
                et l'on souhaite filtrer la requête par rapport aux deux
        '''

        if model_attribute := cache_custom_getattr.get(field_name):
            return model_attribute, query

        if '.' not in field_name:

            # cas simple
            model_attribute = getattr(Model, field_name)

            # mise en cache
            cache_custom_getattr['field_name'] = model_attribute
            return model_attribute, query

        else:

            # cas avec un seul . => a.b
            # on verra ensuite si on à le besoin de le faire récursivement

            (rel, col) = field_name.split('.')

            relationship = getattr(Model, rel)

            alias = orm.aliased(relationship.mapper.entity)  # Model ?????

            if query:
                query = query.join(alias, relationship)

            model_attribute = getattr(alias, col)

            # mise en cache
            cache_custom_getattr['field_name'] = model_attribute

            return model_attribute, query

    def get_sorters(self, Model, sorters, query):
        order_bys = []

        for s in sorters:
            s_field = s['field']
            s_dir = s['dir']
            model_attribute, query = self.custom_getattr(Model, s_field, query)
            if model_attribute is None:
                continue

            order_by = (
                model_attribute.desc() if s_dir == 'desc'
                else
                model_attribute.asc()
            )

            order_bys.append(order_by)

        return order_bys

    def process_sorters(self, Model, sorters, query):
        '''
            process sorters (ORDER BY)
        '''

        order_bys = self.get_sorters(Model, sorters, query)
        if order_bys:
            query = query.order_by(*(tuple(order_bys)))
        return query

    # def get_row_number_from_value(self, value, query):

    #     field_name = self.pk_field_name()
    #     # res = query.filter(getattr(self.Model(), field_name) == value).one()
    #     # query.row_number().over()
    #     res = query.filter(getattr(self.Model(), field_name) == value).one()

    #     return res

    def process_page_size(self, page, size, value, query):
        '''
        LIMIT et OFFSET
        '''

        # if value:
        #     row_number = self.get_row_number_from_value(value, query)
        if size and int(size) > 0:
            query = query.limit(size)

            if page and int(page) > 1:
                offset = (int(page) - 1) * int(size)
                print('offset', offset)
                query = query.offset(offset)

        return query
