'''
    sqla query functions
'''

from sqlalchemy import cast, orm, and_, or_, not_

from geonature.utils.env import DB

from .errors import (
    SchemaRepositoryFilterError,
    SchemaRepositoryFilterTypeError,
)

'''
    pour ne pas faire 2 alias sur le même
'''
cache_custom_getattr = {}


def reset_cache_custom_getattr():
    print('reset_cache')
    cache_custom_getattr = {}


def custom_getattr(Model, field_name, query=None):
    '''
        getattr pour un modèle, étendu pour pouvoir traiter les 'rel.field_name'

        on utilise des alias pour pouvoir gérer les cas plus compliqués

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


def process_filters(Model, filters, query):
    '''
        process filter

        TODO dict entry
        {
            a: f1,
            b: f2,
            c: f3,
            d: f4,
            e: f5,
            cond: '!a*(b+c*!(de))'
        }
    '''

    filters_processed, query = process_filter_array(Model, filters, query)

    if filters_processed is not None:
        return query.filter(filters_processed)

    return query


def process_filter_array(Model, filter_array, query):
    '''
        process filter list

        traite un liste qui peux contenir
            - des listes (traitement récursif)
            - des filtres : { field : <f_field>, type: <f_type>, value: <f_value>}
            - des operateurs :
                - '!' : négation, unitaire
                - '*' : et
                - '+ : ou

        l'opérateur par défaut est '*':

        exemples (f1 et f2 sont des filtres):

            - [ f1, '*', f2]                  =>  f1 ET f2
            - [ f1, '+', f2]                  =>  f1 OU f2
            - [ f1, f2]                       =>  f1 ET f2
            - [ '!', f1, '+', '!', f2]        =>  (NON f1) OU (NON f2)
            - [ '!', [ f1, '+', '!', f2 ] ]   =>  NON (f1 OU (NON f2))
    '''
    cur_filter = None
    cur_ops = []

    for elem in filter_array:

        f = None

        # récursivité sur les listes
        if type(elem) is list:
            f, query = process_filter_array(elem, query)

        # filtre
        elif type(elem) is dict:
            f, query = get_filter(Model, elem, query)

        # operation
        elif elem in '!+*':
            # deux négations '!' s'annulent
            if elem == '!' and len(cur_ops) and cur_ops[-1] == '!':
                cur_ops = cur_ops[:-1]
            else:
                cur_ops.append(elem)

        else:
            raise SchemaRepositoryFilterError("L'élément de liste de filtre {} est mal défini.".format(elem))

        if f is not None:

            # on prend le dernier opérateur de la liste ou bien '*' par défaut
            op = (len(cur_ops) and cur_ops.pop()) or "*"

            # traitement de la négation '!'
            if op == '!':
                f = not_(f)
                # on prend le dernier opérateur de la liste ou bien '*' par défaut
                op = (len(cur_ops) and cur_ops.pop()) or "*"

            # s'il y un filtre courant, on applique l'opération en cours
            if cur_filter is not None:
                if op == '*':
                    cur_filter = and_(cur_filter, f)
                if op == '+':
                    cur_filter = or_(cur_filter, f)

            # s'il n'y a pas de filtre courant, on initialise la variable cur_filter
            else:
                cur_filter = f

    return cur_filter, query


def get_filter(Model, f, query):

    filter_out = None

    f_field = f['field']
    f_type = f['type']
    f_value = f['value']

    model_attribute, query = custom_getattr(Model, f_field, query)

    # si besoin de redefinir type

    if f_type == 'like':
        filter_out = (
            cast(model_attribute, DB.String)
            .like('%{}%'.format(f_value))
        )

    elif f_type == 'ilike':
        filter_out = (
            cast(model_attribute, DB.String)
            .ilike('%{}%'.format(f_value))
        )

    elif f_type == 'eq':
        filter_out = (
            cast(model_attribute, DB.String)
            == (f_value)
        )

    elif f_type == 'in':
        filter_out = (
            cast(model_attribute, DB.String)
            .in_(
                map(
                    lambda x: str(x),
                    f_value
                )
            )
        )

    else:
        raise SchemaRepositoryFilterTypeError("Le type de filtre {} n'est pas géré".format(f_type))

    return filter_out, query


def process_sorters(Model, sorters, query):
    '''
        process sorters (ORDER BY)
    '''

    order_bys = []

    for s in sorters:
        s_field = s['field']
        s_dir = s['dir']
        model_attribute, query = custom_getattr(Model, s_field, query)
        if model_attribute is None:
            continue

        order_by = (
            model_attribute.desc() if s_dir == 'desc'
            else
            model_attribute.asc()
        )

        order_bys.append(order_by)

    if order_bys:
        query = query.order_by(*(tuple(order_bys)))

    return query


def process_page_size(page, size, query):
    '''
    LIMIT et OFFSET
    '''

    if size and int(size) > 0:
        query = query.limit(size)
        if page and int(page) > 1:
            query = query.offset((int(page) - 1) * int(size))

    return query
