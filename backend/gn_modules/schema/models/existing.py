from .. import errors

from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes
from pypnusershub.db.models import User, Organisme, Application, Profils, UserApplicationRight
from geonature.core.gn_commons.models.base import CorModuleDataset, TModules, TMedias, BibTablesLocation
from geonature.core.gn_meta.models import TDatasets, TAcquisitionFramework, CorAcquisitionFrameworkActor, CorDatasetActor
from geonature.core.gn_synthese.models import Synthese
from geonature.core.gn_permissions.models import TActions, TFilters, TObjects, CorRoleActionFilterModuleObject
from ref_geo.models import LAreas, BibAreasTypes, BibLinearsTypes, LLinears, TLinearGroups
from geonature.core.taxonomie.models import Taxref
from geonature.core.users.models import CorRole

from geonature.utils.env import db

cache_existing_models = {
    "commons.module": TModules,
    "commons.module_jdd": CorModuleDataset,
    "commons.media": TMedias,
    "commons.table_location": BibTablesLocation,
    "meta.actor": CorDatasetActor,
    "meta.ca": TAcquisitionFramework,
    "meta.jdd": TDatasets,
    "perm.action": TActions,
    "perm.filter": TFilters,
    "perm.object": TObjects,
    "perm.permission": CorRoleActionFilterModuleObject,
    "ref_geo.linear": LLinears,
    "ref_geo.linear_group": TLinearGroups,
    "ref_geo.linear_type": BibLinearsTypes,
    "ref_geo.area": LAreas,
    "ref_geo.area_type": BibAreasTypes,
    "ref_nom.nomenclature": TNomenclatures,
    "ref_nom.type": BibNomenclaturesTypes,
    "syn.synthese": Synthese,
    "tax.taxref": Taxref,
    "user.app": Application,
    "user.app_profil": UserApplicationRight,
    "user.groupe": CorRole,
    "user.organisme": Organisme,
    "user.profil": Profils,
    "user.role": User,

}

class SchemaModelExisting():

    def get_model_from_schema_dot_table(self, schema_dot_table):

        Model = cache_existing_models.get(self.schema_name())

        if Model:
            return Model

        for Model in db.Model._decl_class_registry.values():
            if not (isinstance(Model, type) and issubclass(Model, db.Model)):
                continue

            sql_table_name = Model.__tablename__
            sql_schema_name = Model.__table__.schema

            if '{}.{}'.format(sql_schema_name, sql_table_name) == schema_dot_table:
                return Model


    def search_existing_model(self):
        Model = None
        for Model_ in db.Model._decl_class_registry.values():
            if isinstance(Model_, type) and issubclass(Model_, db.Model):
                if self.model_name() == Model_.__name__:
                    Model = Model_
        return Model

    def get_existing_model(self):
        '''
        '''
        Model = cache_existing_models.get(self.schema_name())

        if not Model:
            Model = self.search_existing_model()
            # return None

        if not Model:
            return None

        for key, column_def in self.columns().items():
            if hasattr(Model, key):
                self.process_existing_column_model(key, column_def, getattr(Model, key))
                # continue
            else:
                setattr(Model, key, self.process_column_model(column_def))

        # store in cache before relation (avoid circular dependancies)
        self.cls.set_schema_cache(self.schema_name(), 'model', Model)

        for key, relation_def in self.relationships().items():
            if hasattr(Model, key):
                continue

            setattr(Model, key, self.process_relation_model(key, relation_def, Model))

        return Model
# from ..cache import cache_schemas
