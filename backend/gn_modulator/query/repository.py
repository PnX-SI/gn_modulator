import sqlalchemy as sa
from .getattr import clear_query_cache
from .field import process_fields
from .utils import get_sorters, process_additional_columns, process_page_size
from .permission import process_filter_permission
from .filters import process_filters


def query_list(Model, module_code, action, params, query_type, id_role=None):
    """
    methode pour générer une requete de liste

    - Model: class de modèle sqlalchemy
    - module_code: de module (pour les permissions)
    - action: CRUVED
    - params: dictionnaire ayant pour clé
        - fields
        - filters
        - prefilters
        - sort
        - ...
    - query_type: valeurs possibles:
        - 'select' ou None
        - 'update'
        - 'delete'
        - 'page_number'
        - 'total' : requête destinée au count avant filters
        - 'filtered' : requête destinée au count avant filters
    - id_role: pour les permission

    TODO ajout permission_object_code ??
    """
    query = Model.query

    model_pk_fields = [getattr(Model, pk_field_name) for pk_field_name in Model.pk_field_names()]

    query = query.options(sa.orm.load_only(*model_pk_fields))

    # if query_type not in ["update", "delete"]:
    # query = query.distinct()

    query = process_fields(Model, query, params.get("fields") or [])

    # clear_query_cache
    clear_query_cache(query)

    order_bys, query = get_sorters(Model, query, params.get("sort", []))

    # ajout colonnes row_number, scope (cruved)
    query = process_additional_columns(Model, query, params, order_bys, id_role)

    # - prefiltrage permissions (CRUVED sensibilité etc)
    query = process_filter_permission(Model, query, id_role, action, module_code)

    # - prefiltrage params
    query = process_filters(Model, query, params.get("prefilters", []))

    # requete pour count 'total'
    if query_type == "total":
        return query.options(sa.orm.load_only(*model_pk_fields))

    # filtrage
    query = process_filters(Model, query, params.get("filters", []))

    # requete pour count 'filtered'
    if query_type == "filtered":
        return query.options(sa.orm.load_only(*model_pk_fields))

    if query_type in ["update", "delete", "page_number"]:
        return query

    # raise load
    query = query.options(sa.orm.raiseload("*"))

    # sort
    query = query.order_by(*(tuple(order_bys)))

    # limit offset
    query = process_page_size(query, params.get("page"), params.get("page_size"))

    return query
