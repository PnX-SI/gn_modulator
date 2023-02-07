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

cache_existing_tables = {
    "utilisateurs.cor_role_liste": cor_role_liste,
    "utilisateurs.cor_roles": CorRole.__table__,
    "gn_commons.cor_module_dataset": CorModuleDataset.__table__,
}


class SchemaModelExisting:
    def get_cache_existing_tables(self, schema_dot_table):
        return cache_existing_tables.get(schema_dot_table)

    # def get_model_from_schema_dot_table(self, schema_dot_table):
    #     Model = cache_existing_models.get(self.schema_code())

    #     # Patch pourris bug nvelle version gn avec Taxref et Synthese (Taxref)
    #     # TODO arranger existings ??

    #     if self.attr('meta.model'):

    #         model_module_name, model_object_name = self.attr('meta.model').rsplit(".", 1)
    #         model_module = import_module(model_module_name)
    #         Model = getattr(model_module, model_object_name)
    #         return Model

    #     if Model:
    #         return Model

    # for Model in db.Model._decl_class_registry.values():
    #     if not (isinstance(Model, type) and issubclass(Model, db.Model)):
    #         continue

    #     sql_table_name = Model.__tablename__
    #     sql_schema_name = Model.__table__.schema

    #     if "{}.{}".format(sql_schema_name, sql_table_name) == schema_dot_table:
    #         return Model

    # def search_existing_model(self):
    #     Model = None
    #     for Model_ in db.Model._decl_class_registry.values():
    #         if isinstance(Model_, type) and issubclass(Model_, db.Model):
    #             if self.model_name() == Model_.__name__:
    #                 Model = Model_
    #     return Model

    def get_existing_model(self):
        """ """

        model_path = self.attr("meta.model")

        if not model_path:
            return

        Model = get_class_from_path(model_path)

        if not Model:
            raise "error model TODO"

        for key, column_def in self.columns().items():
            if hasattr(Model, key):
                self.process_existing_column_model(key, column_def, getattr(Model, key))
            else:
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
