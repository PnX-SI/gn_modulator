from sqlalchemy import orm
from .base import BaseSchemaQuery
from pypnusershub.db.models import User


class FieldSchemaQuery(BaseSchemaQuery):
    def process_fields(self, fields):
        """
        charge les champs dans la requete (et seulement les champs voulus)

        """

        Model = self.Model()
        fields_to_process = []
        only_fields = []
        for field in fields:
            if not Model.has_property(field):
                continue
            field_to_process, only_field = self.process_field(field)
            if field_to_process not in fields_to_process:
                fields_to_process.append(field_to_process)
            for fo in only_field:
                if fo not in only_fields:
                    only_fields.append(fo)

        # on retire les champs (actors si on a actors.roles)
        field_to_remove_from_process = []
        for f1 in fields_to_process:
            for f2 in fields_to_process:
                if f2.startswith(f1) and "." in f2 and f1 != f2:
                    field_to_remove_from_process.append(f1)

        # champs du modèle
        property_fields = list(
            map(
                lambda x: getattr(Model, x),
                filter(
                    lambda x: "." not in x and not Model.is_relationship(x),
                    fields_to_process,
                ),
            )
        )

        self = self.options(orm.load_only(*property_fields))
        for field in filter(
            lambda x: not (x in field_to_remove_from_process or x in property_fields),
            fields_to_process,
        ):
            _, self = self.getModelAttr(Model, field, only_fields=only_fields)

        return self

    def process_field(self, field):
        Model = self.Model()
        field = Model.cut_key_to_json(field)
        only_field = [field]
        field_to_process = field
        if Model.is_relationship(field):
            rel_schema_code = self.property(field)["schema_code"]
            rel = self.cls(rel_schema_code)
            default_field_names = rel.default_fields()
            only_field = default_field_names

        elif "." in field:
            field_to_process = ".".join(field.split(".")[:-1])
            if field.endswith(".nom_complet") and Model == User:
                only_field.extend(
                    [f"{field_to_process}.prenom_role", f"{field_to_process}.nom_role"]
                )

        # patch nom_complet User

        if field == "nom_complet" and Model == User:
            only_field.extend(["prenom_role", "nom_role"])

        return field_to_process, only_field

    def eager_load_only(self, field_name, only_fields, index):
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
            cache = self.get_query_cache(key_cache_eager)
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
                relation_Model = self.Model().relation_Model(key_cache_eager)
                only_columns_i = [
                    getattr(cache["relation_alias"], pk_field_name)
                    for pk_field_name in relation_Model.pk_field_names()
                ]

            # chargement de relation en eager et choix des champs
            self = self.options(orm.contains_eager(*eagers).load_only(*only_columns_i))

        return self
