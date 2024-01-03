import re
import sqlalchemy as sa
from .getattr import getModelAttr
from .permission import add_column_scope
import sqlparse


def pretty_sql(query):
    txt = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
    txt = txt.replace("%%", "%")
    txt = sqlparse.format(txt, reindent=True, keywordcase="upper")
    return txt


def get_sorters(Model, query, sorts):
    order_bys = []

    for sort in sorts:
        sorters, query = get_sorter(Model, query, sort)
        order_bys.extend(sorters)

    return order_bys, query


def get_sorter(Model, query, sorter):
    orders_by = []
    sort_dir = "-" if "-" in sorter else "+"
    sort_spe = "str_num" if "*" in sorter else "num_str" if "%" in sorter else None
    sort_field = sorter
    for c in "+-%*":
        sort_field = sort_field.replace(c, "")

    model_attribute, query = getModelAttr(Model, query, sort_field)

    if model_attribute is None:
        raise Exception(f"Pb avec le tri {Model}, field: {sort_field}")

    if sort_spe is not None:
        sort_string = sa.func.substring(model_attribute, "[a-zA-Z]+")
        sort_number = sa.cast(sa.func.substring(model_attribute, "[0-9]+"), sa.Numeric)

        if sort_spe == "str_num":
            orders_by.extend([sort_string, sort_number])
        else:
            orders_by.extend([sort_number, sort_string])

    orders_by.append(model_attribute)

    orders_by = [
        sa.nullslast(order_by.desc() if sort_dir == "-" else order_by.asc())
        for order_by in orders_by
    ]

    return orders_by, query


def process_page_size(query, page, page_size):
    """
    LIMIT et OFFSET
    """

    if page_size and int(page_size) > 0:
        query = query.limit(page_size)

        if page and int(page) > 1:
            offset = (int(page) - 1) * int(page_size)
            query = query.offset(offset)

    return query


def process_additional_columns(Model, query, params, order_by, id_role):
    """
    permet d'ajouter de colonnes selon les besoin
    - scope pour cruved (toujours?)
    - row_number (si dans fields)
    """

    fields = params.get("fields") or []

    # cruved
    if "scope" in fields:
        query = add_column_scope(Model, query, id_role)

    # row_number
    if "row_number" in fields:
        query = query.add_columns(sa.func.row_number().over(order_by=order_by).label("row_number"))

    return query
