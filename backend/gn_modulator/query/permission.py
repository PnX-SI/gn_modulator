import sqlalchemy as sa
from geonature.core.gn_permissions.tools import get_scope
from geonature.core.gn_permissions.tools import get_permissions


def add_subquery_scope(Model, query, id_role):
    # test si la methode existe
    if not hasattr(Model, "subquery_scope"):
        return Model

    # test si la sous requete est deja ajoutée
    if hasattr(query, "_subquery_scope"):
        return query

    subquery_scope = Model.subquery_scope(id_role).cte("scope")

    query = query.join(
        subquery_scope,
        getattr(subquery_scope.c, Model.pk_field_name()) == getattr(Model, Model.pk_field_name()),
    )
    query._subquery_scope = subquery_scope
    return query


def add_column_scope(Model, query, id_role):
    """
    ajout d'une colonne 'scope' à la requête
    afin de
        - filter dans la requete de liste
        - verifier les droit sur un donnée pour les action unitaire (post update delete)
        - le rendre accessible pour le frontend
            - affichage de boutton, vérification d'accès aux pages etc ....
    """

    if not hasattr(Model, "subquery_scope"):
        query = query.add_columns(
            sa.sql.literal_column("0", type_=sa.sql.sqltypes.INTEGER).label("scope")
        )
    else:
        query = add_subquery_scope(Model, query, id_role)
        query = query.add_columns(query._subquery_scope.c.scope)

    return query


def process_filter_permission(Model, query, id_role, action, module_code):
    if not id_role:
        return query

    if not hasattr(Model, "permission_filter"):
        return query

    scope_for_action = get_scope(
        action, id_role=id_role, module_code=module_code, bypass_warning=True
    )

    permissions = get_permissions(action, id_role, module_code)
    sensitivity = any([perm.sensitivity_filter for perm in permissions])

    permission_filter, query = Model.permission_filter(
        query, id_role, scope_for_action, sensitivity
    )

    if permission_filter is not None:
        query = query.filter(permission_filter)

    return query
