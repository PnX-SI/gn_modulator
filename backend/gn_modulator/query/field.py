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
                filter(lambda x: "." not in x and not Model.is_relationship(x), fields_to_process),
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
            relation_Model = Model.relation_Model(field)
            default_field_names = relation_Model.default_fields
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
