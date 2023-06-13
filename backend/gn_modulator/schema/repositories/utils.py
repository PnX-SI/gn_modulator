from sqlalchemy import orm, and_, nullslast
from sqlalchemy.orm import load_only, Load
from gn_modulator.utils.commons import getAttr


class SchemaRepositoriesUtil:
    """
    custom getattr: retrouver les attribut d'un modele ou des relations du modèles
    """

    __abstract__ = True

    def set_query_cache(self, query, key, value):
        if not query:
            return
        query._cache = hasattr(query, "_cache") and query._cache or {}
        query._cache[key] = value
        return query

    def clear_query_cache(self, query):
        if hasattr(query, "_cache"):
            delattr(query, "_cache")

    def get_query_cache(self, query, key):
        if not query:
            return
        if not hasattr(query, "_cache"):
            return None
        return query._cache.get(key)

    def process_custom_getattr_res(self, res, query, field_name, index, only_fields=[]):
        # si c'est une propriété
        fields = field_name.split(".")
        is_relationship = self.is_val_relationship(res["val"])
        is_last_field = index == len(fields) - 1

        if not is_relationship:
            # on ne peut pas avoir de field apres une propriété
            if not is_last_field:
                raise Exception(f"pb fields {field_name}, il ne devrait plus rester de champs")

            return res["val"], query

        if not is_last_field:
            return self.custom_getattr(
                res["relation_alias"],
                field_name,
                index=index + 1,
                query=query,
                only_fields=only_fields,
            )

        return res["relation_alias"], query

    def eager_load_only(self, field_name, query, only_fields, index):
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
            cache = self.get_query_cache(query, key_cache_eager)
            eager_i = cache["val_of_type"]
            eagers.append(eager_i)

            # calcul des colonnes
            only_columns_i = list(
                map(
                    lambda x: getattr(
                        cache["relation_alias"], x.replace(f"{key_cache_eager}.", "")
                    ),
                    filter(
                        lambda x: key_cache_eager in x
                        and "." not in x.replace(f"{key_cache_eager}.", "")
                        and hasattr(
                            getattr(cache["relation_alias"], x.replace(f"{key_cache_eager}.", "")),
                            "property",
                        ),
                        only_fields,
                    ),
                ),
            )
            if not only_columns_i:
                rel_schema_code = self.property(key_cache_eager)["schema_code"]
                rel = self.cls(rel_schema_code)
                only_columns_i = [
                    getattr(cache["relation_alias"], pk_field_name)
                    for pk_field_name in rel.pk_field_names()
                ]

            # chargement de relation en eager et choix des champs
            query = query.options(orm.contains_eager(*eagers).load_only(*only_columns_i))

        return query

    def is_val_relationship(self, val):
        return hasattr(val, "mapper") and hasattr(val.mapper, "entity")

    def custom_getattr(
        self, Model, field_name, query=None, only_fields="", index=0, condition=None
    ):
        # liste des champs 'rel1.rel2.pro1' -> 'rel1', 'rel2', 'prop1'
        fields = field_name.split(".")

        # champs courrant (index)
        current_field = fields[index]

        # clé pour le cache
        cache_key = ".".join(fields[: index + 1])

        # test si c'est le dernier champs
        is_last_field = index == len(fields) - 1

        # récupération depuis le cache associé à la query
        res = self.get_query_cache(query, cache_key)
        if res:
            return self.process_custom_getattr_res(res, query, field_name, index, only_fields)

        # si non en cache
        # on le calcule

        # dictionnaire de résultat pour le cache
        res = {
            # "field_name": field_name,
            # "index": index,
            # "is_last_field": is_last_field,
            "val": getattr(Model, current_field),
        }

        # res["is_relationship"] = hasattr(res["val"], "mapper") and hasattr(
        #     res["val"].mapper, "entity"
        # )

        # si c'est une propriété
        if self.is_val_relationship(res["val"]):
            res["relation_model"] = res["val"].mapper.entity
            res["relation_alias"] = orm.aliased(res["relation_model"])
            res["val_of_type"] = res["val"].of_type(res["relation_alias"])
            query = query.join(res["val_of_type"], isouter=True)

        if only_fields:
            query = self.set_query_cache(query, cache_key, res)

        # chargement des champs si is last field
        if self.is_val_relationship(res["val"]) and is_last_field and only_fields:
            # mise en cache seulement dans ce cas
            # query = self.set_query_cache(query, cache_key, res)
            query = self.eager_load_only(field_name, query, only_fields, index)

        # retour
        return self.process_custom_getattr_res(res, query, field_name, index, only_fields)

    def get_sorters(self, Model, sort, query):
        order_bys = []

        for s in sort:
            sort_dir = "+"
            sort_field = s
            if s[-1] == "-":
                sort_field = s[:-1]
                sort_dir = s[-1]

            model_attribute, query = self.custom_getattr(Model, sort_field, query)

            if model_attribute is None:
                continue

            order_by = model_attribute.desc() if sort_dir == "-" else model_attribute.asc()

            # nullslast
            order_by = nullslast(order_by)
            order_bys.append(order_by)

        return order_bys, query

    def get_sorter(self, Model, sorter, query):
        sort_field = sorter["field"]
        sort_dir = sorter["dir"]

        model_attribute, query = self.custom_getattr(Model, sort_field, query)

        order_by = model_attribute.desc() if sort_dir == "desc" else model_attribute.asc()

        order_by = nullslast(order_by)

        return order_by, query

    def process_page_size(self, page, page_size, query):
        """
        LIMIT et OFFSET
        """

        if page_size and int(page_size) > 0:
            query = query.limit(page_size)

            if page and int(page) > 1:
                offset = (int(page) - 1) * int(page_size)
                query = query.offset(offset)

        return query
