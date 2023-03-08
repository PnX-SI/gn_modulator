from geonature.utils.env import db

from .check import ImportMixinCheck
from .data import ImportMixinData
from .insert import ImportMixinInsert
from .mapping import ImportMixinMapping
from .process import ImportMixinProcess
from .raw import ImportMixinRaw
from .relation import ImportMixinRelation
from .update import ImportMixinUpdate
from .utils import ImportMixinUtils


class ImportMixin(
    ImportMixinRelation,
    ImportMixinCheck,
    ImportMixinData,
    ImportMixinInsert,
    ImportMixinMapping,
    ImportMixinProcess,
    ImportMixinRaw,
    ImportMixinUpdate,
    ImportMixinUtils,
):
    def process_import_schema(self, _insert_data=False):
        self._insert_data = _insert_data

        self.init_import()
        if self.errors:
            return self
        db.session.flush()

        self.process_data_table()
        if self.errors:
            return self
        db.session.flush()

        self.process_mapping_view()
        if self.errors:
            return self
        db.session.flush()

        self.process_raw_view()
        if self.errors:
            return self
        db.session.flush()

        self.process_view()
        if self.errors:
            return self
        db.session.flush()

        self.process_check()
        if self.errors:
            return self
        db.session.flush()

        self.process_insert()
        if self.errors:
            return self
        db.session.flush()

        self.process_update()
        if self.errors:
            return self
        db.session.flush()

        self.process_relations()
        if self.errors:
            return self
        db.session.flush()

        self.res["nb_unchanged"] = (
            self.res["nb_process"] - self.res["nb_insert"] - self.res["nb_update"]
        )

        return self
