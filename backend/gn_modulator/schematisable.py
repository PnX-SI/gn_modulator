class ModelPropertyError(Exception):
    pass


class ModelPropertyNomenclatureError(ModelPropertyError):
    pass


import sqlalchemy as sa


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

                # en cas de JSON on stoppe ici
                if hasattr(rel_prop, "type") and str(rel_prop.type) == "JSONB":
                    return rel_prop

                # modele associé à la relation
                relation_Model = rel_prop.mapper.entity
                if not hasattr(relation_Model, "schematisable"):
                    relation_Model = schematisable(relation_Model)
                # clé restante
                remaining_key = ".".join(key.split(".")[1:])

                # propriété associée à la clé restante
                return relation_Model.property(remaining_key)

            if not hasattr(cls, key):
                raise ModelPropertyError(f"Le modèle {cls} n'a pas de cle ({key})")

            return getattr(cls, key)

        @classmethod
        def sql_type(cls, key):
            if not hasattr(cls.property(key), "type"):
                return None
            if isinstance(cls.property(key).type, sa.sql.sqltypes.NullType):
                return None

            sql_type = str(cls.property(key).type)
            if "VARCHAR" in sql_type:
                sql_type = "VARCHAR"
            if "TEXT" == sql_type:
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
            except Exception as e:
                return False

        @classmethod
        def is_relationship(cls, key):
            """
            Renvoie True si la propriété décrite par key est une relation
            """
            res = (
                cls.has_property(key)
                and hasattr(cls.property(key), "property")
                and isinstance(
                    cls.property(key).property, sa.orm.relationships.RelationshipProperty
                )
            )

            return res

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
            return (
                cls.is_relationship(key)
                and cls.property(key).property.direction.name == "ONETOMANY"
            )

        @classmethod
        def relation_Model(cls, key):
            if cls.is_relationship(key):
                return cls.property(key).mapper.entity
            if cls.is_foreign_key(key):
                return cls.property(key).target

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
            return isinstance(prop.property, sa.orm.properties.ColumnProperty)

        @classmethod
        def is_foreign_key(cls, key):
            return cls.is_column(key) and (
                cls.property(key).foreign_keys
                or (
                    hasattr(cls.property(key), "foreign_key")
                    and getattr(cls.property(key), "foreign_key")
                )
            )

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
                if self.sql_type(current_key) == "JSONB":
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
        cls_shematisable.sql_schema_dot_table = sql_schema_dot_table
        cls_shematisable.relation_Model = relation_Model
        cls_shematisable.cor_schema_dot_table = cor_schema_dot_table
        cls_shematisable.sql_type = sql_type
        cls_shematisable.get_nomenclature_type = get_nomenclature_type
        return cls_shematisable

    return _schematisable


def schematisable(*args, **kwargs):
    return get_schematisable_decorator()(args[0])
