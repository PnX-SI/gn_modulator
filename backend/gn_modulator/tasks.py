from celery.utils.log import get_task_logger
from geonature.utils.celery import celery_app
from gn_modulator.imports.models import TImport
from geonature.utils.env import db

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def process_import(self, id_import):
    logger.info("process_import task")
    self.update_state(state="PROGRESS")
    logger.info(db.engine.url)
    logger.info(f"process_import task init {id_import}")
    req = db.session.query(TImport).filter(TImport.id_import == id_import)
    impt = req.one()
    impt.process_import_schema()
