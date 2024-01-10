from celery.utils.log import get_task_logger
from geonature.utils.celery import celery_app
from gn_modulator.imports.models import TImport
from geonature.utils.env import db

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def process_import(self, id_import):
    self.update_state(state="PROGRESS")
    req = db.session.query(TImport).filter(TImport.id_import == id_import)
    impt = req.one()
    impt._logger = logger
    impt.process_import_schema()
