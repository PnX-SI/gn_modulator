from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes
from pypnusershub.db.models import (
    cor_role_liste,
)
from geonature.core.gn_commons.models.base import (
    CorModuleDataset,
)
from geonature.core.users.models import CorRole

from geonature.utils.env import db

from gn_modulator.utils.cache import set_global_cache

from gn_modulator.utils.commons import get_class_from_path
from gn_modulator.query import SchemaQuery

from gn_modulator.schematisable import schematisable

cache_existing_tables = {
    "utilisateurs.cor_role_liste": cor_role_liste,
    "utilisateurs.cor_roles": CorRole.__table__,
    "gn_commons.cor_module_dataset": CorModuleDataset.__table__,
}


class SchemaModelExisting:
    def get_cache_existing_tables(self, schema_dot_table):
        return cache_existing_tables.get(schema_dot_table)

    def get_existing_model(self):
        """ """

        model_path = self.attr("meta.model")

        if not model_path:
            return

        Model = get_class_from_path(model_path)
        # ajout de methodes
        Model = schematisable(Model)

        try:
            Model.query_class = type(
                f"{self.model_name()}SchemaQuery", (SchemaQuery, Model.query_class), {}
            )
        except:
            Model.query_class = type(
                f"{self.model_name()}SchemaQuery", (Model.query_class, SchemaQuery), {}
            )

        if not Model:
            raise "error model TODO"

        for key, column_def in self.columns().items():
            if not hasattr(Model, key) and not column_def.get("column_property"):
                setattr(Model, key, self.process_column_model(key, column_def))

        # store in cache before relation (avoid circular dependencies)
        set_global_cache(["schema", self.schema_code(), "model"], Model)

        for key, relation_def in self.relationships().items():
            if hasattr(Model, key):
                continue

            setattr(Model, key, self.process_relation_model(key, relation_def, Model))

        # process column properties
        for key, column_property_def in self.column_properties().items():
            setattr(
                Model,
                key,
                self.process_column_property_model(key, column_property_def, Model),
            )

        return Model
