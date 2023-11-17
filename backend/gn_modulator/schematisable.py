class ModelPropertyError(Exception):
    pass


class ModelPropertyNomenclatureError(ModelPropertyError):
    pass


from sqlalchemy import orm


def get_schematisable_decorator():
    def _schematisable(cls_shematisable):
        @classmethod
        def property(cls, key):
            """
            - renvoie la propriete Model.key, ou Model.rel
            - key peut comporter des . comme par exemple rel1.key1
              dans ce cas propery est appelée récusrivement pour avoir le champ key1 de la relation rel1
            """

            if "." in key:
                # cle associée à la relation
                rel_key = key.split(".")[0]
                # propriete associée à la relation
                rel_prop = cls.property(rel_key)
                # modele associé à la relation
                rel_Model = rel_prop.mapper.entity

                # en cas de JSON on stoppe ici
                if rel_prop.type == "JSONB":
                    return rel_prop

                # clé restante
                remaining_key = ".".join(key.split(".")[1:])

                # propriété associée à la clé restante
                return rel_Model.property(remaining_key)

            if not hasattr(cls, key):
                raise ModelPropertyError(f"Le modèle {cls} n'a pas de cle {rel_prop} ({key})")

            return getattr(cls, key)

        @classmethod
        def sql_type(cls, key):
            sql_type = str(cls.property(key).type)
            if "VARCHAR" in sql_type:
                sql_type = "VARCHAR"
            if sql_type == "DATETIME":
                sql_type = "TIMESTAMP"
            if "GEOMETRY" in sql_type:
                sql_type = "GEOMETRY"
            return sql_type

        @classmethod
        def has_property(cls, key):
            """
            Renvoie True si la propriété décrite par key existe
            """
            try:
                cls.property(key)
                return True
            except:
                return False

        @classmethod
        def is_relationship(cls, key):
            """
            Renvoie True si la propriété décrite par key est une relation
            """
            return cls.has_property(key) and isinstance(
                cls.property(key).property, orm.relationships.RelationshipProperty
            )

        @classmethod
        def is_relation_n_n(cls, key):
            """
            Renvoie True si la propriété décrite par key est une relation
            """
            return (
                cls.is_relationship(key)
                and cls.property(key).property.direction.name == "MANYTOMANY"
            )

        @classmethod
        def is_relation_1_n(cls, key):
            """
            Renvoie True si la propriété décrite par key est une relation
            """
            return cls.is_relationship(key) and cls.property(key).direction.name == "ONETOMANY"

        @classmethod
        def relation_Model(cls, key):
            return cls.is_relationship(key) and cls.property(key).mapper.entity or None

        @classmethod
        def cor_schema_dot_table(cls, key):
            if not cls.is_relation_n_n(key):
                return None

            relation = cls.property(key).property
            return f"{relation.secondary.schema}.{relation.secondary.name}"

        @classmethod
        def is_column(cls, key):
            if not cls.has_property(key):
                return False

            prop = cls.property(key)
            return isinstance(prop.property, orm.properties.ColumnProperty)

        @classmethod
        def is_foreign_key(cls, key):
            return cls.is_column(key) and cls.property(key).foreign_keys

        @classmethod
        def is_primary_key(cls, key):
            if not cls.is_column(key):
                return False

            prop = cls.property(key)
            return prop.primary_key

        @classmethod
        def cut_key_to_json(self, key):
            """
            renvoie le champs json de la variable key
            """
            keys = key.split(".")
            for index, k in enumerate(keys):
                current_key = ".".join(keys[: index + 1])
                if self.property(current_key).type == "JSONB":
                    return current_key
            return key

        @classmethod
        def pk_field_names(cls):
            """
            renvoie la liste des clé primaires
            """
            return list(map(lambda x: x.key, cls.__mapper__.primary_key))

        @classmethod
        def pk_field_name(cls):
            """
            checks primary key uniqueness and returns it
            """
            pk_field_names = cls.pk_field_names()
            return pk_field_names[0] if len(pk_field_names) == 1 else None

        @classmethod
        def sql_schema_dot_table(cls):
            return f"{cls.__table__.schema}.{cls.__tablename__}"

        @classmethod
        def get_nomenclature_type(cls, key):
            property = cls.property(key)
            code_type = hasattr(property, "nomenclature_type") and property.nomenclature_type
            if hasattr(property, "nomenclature_type") and not (code_type):
                raise ModelPropertyNomenclatureError(
                    f"Le type de nomenclature pour {cls.sql_schema_dot_table()}.{key} n'a pas été trouvé"
                )
            return code_type

        @classmethod
        def getModelAttr(
            cls,
            field_name,
            query=None,
            only_fields="",
            index=0,
        ):
            """ """

            # liste des champs 'rel1.rel2.pro1' -> 'rel1', 'rel2', 'prop1'
            fields = field_name.split(".")

            # champs courrant (index)
            current_field = fields[index]

            # clé pour le cache
            cache_key = ".".join(fields[: index + 1])

            is_relationship = cls.is_relationship(cache_key)

            # test si c'est le dernier champs
            is_last_field = index == len(fields) - 1

            # récupération depuis le cache associé à la query
            if hasattr(query, "get_query_cache"):
                res = query.get_query_cache(cache_key)

                if res:
                    return cls.process_getattr_res(res, query, field_name, index, only_fields)
            # si non en cache
            # on le calcule

            # dictionnaire de résultat pour le cache
            res = {
                "val": getattr(cls, current_field),
            }

            # si c'est une propriété
            if is_relationship:
                res["relation_model"] = res["val"].mapper.entity
                if not hasattr(res["relation_model"], "is_schematisable"):
                    res["relation_model"] = schematisable(res["relation_model"])
                res["relation_alias"] = (
                    orm.aliased(res["relation_model"]) if query else res["relation_model"]
                )
                res["val_of_type"] = res["val"].of_type(res["relation_alias"])
                if query:
                    # toujours en outer ???
                    query = query.join(res["val_of_type"], isouter=True)

            if only_fields:
                query = query.set_query_cache(cache_key, res)

            # chargement des champs si is last field
            if is_relationship and is_last_field and only_fields:
                query = query.eager_load_only(field_name, query, only_fields, index)

            # retour
            return cls.process_getattr_res(res, query, field_name, index, only_fields)

        @classmethod
        def process_getattr_res(
            cls,
            res,
            query,
            field_name,
            index,
            only_fields=[],
        ):
            # si c'est une propriété
            fields = field_name.split(".")
            # clé pour le cache
            cache_key = ".".join(fields[: index + 1])

            is_relationship = cls.is_relationship(cache_key)
            is_last_field = index == len(fields) - 1

            if not is_relationship:
                # on ne peut pas avoir de field apres une propriété
                if not is_last_field:
                    raise Exception(f"pb fields {field_name}, il ne devrait plus rester de champs")
                return res["val"], query

            if not is_last_field:
                if not query:
                    query = (
                        orm.and_(query, res["val"].expression) if query else res["val"].expression
                    )

                return res["relation_alias"].getModelAttr(
                    field_name,
                    index=index + 1,
                    query=query,
                    only_fields=only_fields,
                )

            output_field = "val" if is_last_field and is_relationship else "relation_alias"
            return res[output_field], query

        cls_shematisable.is_schematisable = True
        cls_shematisable.pk_field_names = pk_field_names
        cls_shematisable.pk_field_name = pk_field_name
        cls_shematisable.property = property
        cls_shematisable.has_property = has_property
        cls_shematisable.is_relationship = is_relationship
        cls_shematisable.is_relation_n_n = is_relation_n_n
        cls_shematisable.is_relation_1_n = is_relation_1_n
        cls_shematisable.is_foreign_key = is_foreign_key
        cls_shematisable.is_primary_key = is_primary_key
        cls_shematisable.is_column = is_column
        cls_shematisable.cut_key_to_json = cut_key_to_json
        cls_shematisable.getModelAttr = getModelAttr
        cls_shematisable.process_getattr_res = process_getattr_res
        cls_shematisable.sql_schema_dot_table = sql_schema_dot_table
        cls_shematisable.relation_Model = relation_Model
        cls_shematisable.cor_schema_dot_table = cor_schema_dot_table
        cls_shematisable.sql_type = sql_type
        cls_shematisable.get_nomenclature_type = get_nomenclature_type
        return cls_shematisable

    return _schematisable


def schematisable(*args, **kwargs):
    return get_schematisable_decorator()(args[0])
