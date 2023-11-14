import time
from geonature.utils.env import db
from .check import ImportMixinCheck
from .count import ImportMixinCount
from .data import ImportMixinData
from .insert import ImportMixinInsert
from .mapping import ImportMixinMapping
from .process import ImportMixinProcess
from .raw import ImportMixinRaw
from .relation import ImportMixinRelation
from .update import ImportMixinUpdate
from .utils import ImportMixinUtils
from .log import ImportMixinLog


class ImportMixin(
    ImportMixinRelation,
    ImportMixinCheck,
    ImportMixinCount,
    ImportMixinData,
    ImportMixinInsert,
    ImportMixinMapping,
    ImportMixinProcess,
    ImportMixinRaw,
    ImportMixinUpdate,
    ImportMixinLog,
    ImportMixinUtils,
):
    def process_import_schema(self):
        """
        fonction du processus d'import
        """

        self.status = "PROCESSING"
        self.flush_or_commit()

        # boucle sur les étapes
        for step in self.remaining_import_steps():
            self.process_step(step)
            if self.has_errors():
                errors = self.errors
                steps = self.steps
                try:
                    self.flush_or_commit()
                except:
                    db.session.rollback()
                    self.errors = errors
                    self.steps = steps
                    self.status = "ERROR"
                    self.flush_or_commit()
                return

        self.status = "PENDING" if step != self.import_steps()[-1] else "DONE"
        self.flush_or_commit()

        return

    def flush_or_commit(self):
        db.session.flush()
        if not self.options.get("no_commit"):
            db.session.commit()

    def process_step(self, step):
        action = f"process_step_{step}"
        action_start = time.time()
        getattr(self, action)()
        action_end = time.time()
        elapsed_time = action_end - action_start
        self.steps[step] = {"time": elapsed_time}
