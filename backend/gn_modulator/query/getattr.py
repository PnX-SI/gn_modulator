import sqlalchemy as sa
from gn_modulator.schematisable import schematisable


def set_query_cache(query, key, value):
    query._cache = hasattr(query, "_cache") and query._cache or {}
    query._cache[key] = value
    return query


def get_query_cache(query, key):
    if not hasattr(query, "_cache"):
        return None
    return query._cache.get(key)


def clear_query_cache(query):
    if hasattr(query, "_cache"):
        delattr(query, "_cache")
    return query


def getModelAttr(Model, query, field_name, only_fields="", index=0, condition=None):
    """ """

    # liste des champs 'rel1.rel2.pro1' -> 'rel1', 'rel2', 'prop1'
    fields = field_name.split(".")

    # champs courrant (index)
    current_field = fields[index]

    # clé pour le cache
    cache_key = ".".join(fields[: index + 1])

    is_relationship = Model.is_relationship(cache_key)

    # test si c'est le dernier champs
    is_last_field = index == len(fields) - 1

    # récupération depuis le cache associé à la query
    res = get_query_cache(query, cache_key)

    if res:
        return process_getattr_res(
            Model, query, res, field_name, index, only_fields=only_fields, condition=condition
        )
    # si non en cache
    # on le calcule

    # dictionnaire de résultat pour le cache

    current_relation_cache_key = ".".join(fields[:index])

    current_Model = (
        get_query_cache(query, current_relation_cache_key)["relation_alias"]
        if query is not None and current_relation_cache_key
        else (
            Model.relation_Model(current_relation_cache_key)
            if current_relation_cache_key
            else Model
        )
    )

    res = {"val": getattr(current_Model, current_field)}

    # si c'est une propriété
    if is_relationship:
        res["relation_model"] = res["val"].mapper.entity
        if not hasattr(res["relation_model"], "is_schematisable"):
            res["relation_model"] = schematisable(res["relation_model"])
        res["relation_alias"] = (
            sa.orm.aliased(res["relation_model"], name=cache_key)
            if query is not None
            else res["relation_model"]
        )
        res["val_of_type"] = res["val"].of_type(res["relation_alias"])
        if hasattr(query, "join"):
            # toujours en outer ???
            query = query.join(res["val_of_type"], isouter=True)

    if query is not None:
        query = set_query_cache(query, cache_key, res)

    # chargement des champs si is last field
    if is_relationship and is_last_field and only_fields:
        query = eager_load_only(Model, query, field_name, only_fields, index)

    # retour
    return process_getattr_res(
        Model, query, res, field_name, index, only_fields=only_fields, condition=condition
    )


def process_getattr_res(Model, query, res, field_name, index, only_fields=[], condition=None):
    # si c'est une propriété
    fields = field_name.split(".")
    # clé pour le cache
    cache_key = ".".join(fields[: index + 1])

    is_relationship = Model.is_relationship(cache_key)
    is_last_field = index == len(fields) - 1

    if not is_relationship:
        # on ne peut pas avoir de field apres une propriété
        if not is_last_field:
            raise Exception(f"pb fields {field_name}, il ne devrait plus rester de champs")
        return res["val"], query if query is not None else condition

    if not is_last_field:
        if condition is not None:
            condition = sa.and_(condition, res["val"].expression)

        return getModelAttr(
            Model,
            query,
            field_name,
            index=index + 1,
            only_fields=only_fields,
            condition=condition,
        )

    output_field = "val" if is_last_field and is_relationship else "relation_alias"
    return res[output_field], query if query is not None else condition


def eager_load_only(Model, query, field_name, only_fields, index):
    """
    charge les relations et les colonnes voulues
    """

    fields = field_name.split(".")

    # table à charger en eager_load
    eagers = []

    # boucle de 0 à index
    # pour le calcul de eagers et only_columns
    for i in range(0, index + 1):
        # recupération des relations depuis le cache
        key_cache_eager = ".".join(fields[: i + 1])
        cache = get_query_cache(query, key_cache_eager)
        eager_i = cache["val_of_type"]
        eagers.append(eager_i)

        # calcul des colonnes
        only_columns_i = list(
            map(
                lambda x: getattr(cache["relation_alias"], x.replace(f"{key_cache_eager}.", "")),
                filter(
                    lambda x: key_cache_eager in x
                    and x.startswith(f"{key_cache_eager}.")
                    and "." not in x.replace(f"{key_cache_eager}.", "")
                    and hasattr(
                        getattr(cache["relation_alias"], x.replace(f"{key_cache_eager}.", "")),
                        "property",
                    ),
                    only_fields,
                ),
            )
        )
        if not only_columns_i:
            relation_Model = Model.relation_Model(key_cache_eager)
            only_columns_i = [
                getattr(cache["relation_alias"], pk_field_name)
                for pk_field_name in relation_Model.pk_field_names()
            ]
        # chargement de relation en eager et choix des champs
        query = query.options(sa.orm.contains_eager(*eagers).load_only(*only_columns_i))

    return query
