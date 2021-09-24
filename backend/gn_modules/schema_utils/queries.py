'''
    sqla query functions
'''
from sqlalchemy import func, cast, orm, and_
from geonature.utils.env import DB

def custom_getattr(Model, field_name, query):
    '''
        getattr pour un modèle, étendu pour pouvoir traiter les 'rel.field_name'
        TODO Ajouter les relation:
        - ex : rel.rel_name
    '''
    return getattr(Model, field_name), query


def process_filters(Model, filters, query):
    '''
        process filters (WHERE)
        TODO traiter le plus de filtres
    '''
    for f in filters:

        f_field = f['field']
        f_type = f['type'] 
        f_value = f['value']
        
        model_attribute, query = custom_getattr(Model, f_field, query)
        
        if f_type == 'like':
            query = (
                query.filter(
                    cast(model_attribute, DB.String)
                    .like('%{}%'.format(f_value))
                )
            )

    return query

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
            query = query.offset((int(page)-1) * int(size) )

    return query