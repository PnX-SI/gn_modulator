import re
from sqlalchemy import orm, and_, nullslast, func, Numeric, cast
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

    def process_custom_getattr_res(
        self,
        res,
        query,
        condition,
        field_name,
        index,
        only_fields=[],
        output_field="relation_alias",
    ):
        # si c'est une propriété
        fields = field_name.split(".")
        is_relationship = self.is_val_relationship(res["val"])
        is_last_field = index == len(fields) - 1

        if not is_relationship:
            # on ne peut pas avoir de field apres une propriété
            if not is_last_field:
                raise Exception(f"pb fields {field_name}, il ne devrait plus rester de champs")
            return res["val"], query or condition

        if not is_last_field:
            if not query:
                condition = (
                    and_(condition, res["val"].expression) if condition else res["val"].expression
                )
            return self.custom_getattr(
                res["relation_alias"],
                field_name,
                index=index + 1,
                query=query,
                condition=condition,
                only_fields=only_fields,
                output_field=output_field,
            )

        return res[output_field], query or condition

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
                        and x.startswith(f"{key_cache_eager}.")
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
        self,
        Model,
        field_name,
        query=None,
        condition=None,
        only_fields="",
        index=0,
        output_field="relation_alias",
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
            return self.process_custom_getattr_res(
                res, query, condition, field_name, index, only_fields, output_field=output_field
            )

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
            res["relation_alias"] = (
                orm.aliased(res["relation_model"]) if query else res["relation_model"]
            )
            # res["relation_alias"] = orm.aliased(res["relation_model"])
            res["val_of_type"] = res["val"].of_type(res["relation_alias"])
            if query:
                query = query.join(res["val_of_type"], isouter=True)

        if only_fields:
            query = self.set_query_cache(query, cache_key, res)

        # chargement des champs si is last field
        if self.is_val_relationship(res["val"]) and is_last_field and only_fields:
            query = self.eager_load_only(field_name, query, only_fields, index)

        # retour
        return self.process_custom_getattr_res(
            res, query, condition, field_name, index, only_fields, output_field=output_field
        )

    def get_sorters(self, sort, query):
        order_bys = []

        for s in sort:
            sorters, query = self.get_sorter(s, query)
            order_bys.extend(sorters)

        return order_bys, query

    def get_sorter(self, sorter, query):
        orders_by = []
        sort_dir = "-" if "-" in sorter else "+"
        sort_spe = "str_num" if "*" in sorter else "num_str" if "%" in sorter else None
        sort_field = re.sub(r"[+-\\*%]", "", sorter)

        model_attribute, query = self.custom_getattr(self.Model(), sort_field, query)

        if model_attribute is None:
            raise Exception(f"Pb avec le tri {self.schema_code()}, field: {sort_field}")

        if sort_spe is not None:
            sort_string = func.substring(model_attribute, "[a-zA-Z]+")
            sort_number = cast(func.substring(model_attribute, "[0-9]+"), Numeric)

            if sort_spe == "str_num":
                orders_by.extend([sort_string, sort_number])
            else:
                orders_by.extend([sort_number, sort_string])

        orders_by.append(model_attribute)

        orders_by = [
            nullslast(order_by.desc() if sort_dir == "-" else order_by.asc())
            for order_by in orders_by
        ]

        return orders_by, query

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
