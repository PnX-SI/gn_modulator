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

    def get_query_cache(self, query, key):
        if not query:
            return
        if not hasattr(query, "_cache"):
            return None
        return query._cache.get(key)

    def process_custom_getattr_res(self, res, query, only_fields=[]):
        # si c'est une propriété
        if not res["is_relationship"]:
            # on ne peut pas avoir de field apres une propriété
            if not res["is_last_field"]:
                raise Exception(
                    f"pb fields {res['field_name']}, il ne devrait plus rester de champs"
                )

            return res["val"], query

        if not res["is_last_field"]:
            return self.custom_getattr(
                res["relation_alias"],
                res["field_name"],
                index=res["index"] + 1,
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
                only_columns_i = [getattr(cache["relation_alias"], rel.pk_field_name())]

            # chargement de relation en eager et choix des champs
            query = query.options(orm.contains_eager(*eagers).load_only(*only_columns_i))

        return query

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
            return self.process_custom_getattr_res(res, query, only_fields)

        # si non en cache
        # on le calcule

        # dictionnaire de résultat pour le cache
        res = {
            "field_name": field_name,
            "index": index,
            "is_last_field": is_last_field,
            "val": getattr(Model, current_field),
        }

        res["is_relationship"] = hasattr(res["val"], "mapper") and hasattr(
            res["val"].mapper, "entity"
        )

        # si c'est une propriété
        if res["is_relationship"]:
            res["relation_model"] = res["val"].mapper.entity
            res["relation_alias"] = orm.aliased(res["relation_model"])
            res["val_of_type"] = res["val"].of_type(res["relation_alias"])
            query = query.join(res["val_of_type"], isouter=True)

        # mise en cache
        query = self.set_query_cache(query, cache_key, res)

        # chargement des champs si is last field
        if res["is_relationship"] and is_last_field and only_fields:
            query = self.eager_load_only(field_name, query, only_fields, index)

        # mise en cache et retour
        return self.process_custom_getattr_res(res, query, only_fields)

    def custom_getattr2(self, Model, field_name, query=None, condition=None, fields=None):
        """

        obselete

        getattr pour un modèle, étendu pour pouvoir traiter les 'rel.field_name'

        on utilise des alias pour pouvoir gérer les cas plus compliqués

        query pour les filtres dans les api
        condition pour les filtres dans les column_properties

        exemple:

            on a deux relations de type nomenclature
            et l'on souhaite filtrer la requête par rapport aux deux

        TODO gerer plusieurs '.'
        exemple
        http://localhost:8000/modules/schemas.sipaf.pf/rest/?page=1&page_size=13&sorters=[{%22field%22:%22id_pf%22,%22dir%22:%22asc%22}]&filters=[{%22field%22:%22areas.type.coe_type%22,%22type%22:%22=%22,%22value%22:%22DEP%22}]&fields=[%22id_pf%22,%22nom_pf%22,%22ownership%22]
        """

        if "." not in field_name:
            # cas simple
            model_attribute = getattr(Model, field_name)

            return model_attribute, query

        else:
            # cas avec un ou plusieurs '.', recursif

            field_names = field_name.split(".")

            rel = field_names[0]
            relationship = getattr(Model, rel)

            col = ".".join(field_names[1:])

            # pour recupérer le modèle correspondant à la relation
            relation_entity = relationship.mapper.entity

            if query is not None and condition is None:
                # on fait un alias
                relation_entity = orm.aliased(relationship.mapper.entity)
                # relation_entity = relationship.mapper.entity

                if fields:
                    query = query.join(relation_entity, isouter=True)
                else:
                    query = query.join(relation_entity, isouter=True)
                # query = query.join(relation_entity, relationship, isouter=True)
                # if fields:
                # query = query.options(orm.joinedload(relationship).load_only(*fields))
            elif condition:
                # TODO gérer les alias si filtres un peu plus tordus ??
                query = and_(query, relationship._query_clause_element())

            return self.custom_getattr(relation_entity, col, query, condition)

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
