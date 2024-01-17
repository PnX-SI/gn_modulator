from celery.utils.log import get_task_logger
from geonature.utils.celery import celery_app
from gn_modulator.imports.models import TImport
from geonature.utils.env import db
from sqlalchemy import select

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def process_import(self, id_import):
    self.update_state(state="PROGRESS")
    req = select(TImport).where(TImport.id_import == id_import)
    impt = db.session.execute(req).scalar_one()
    impt._logger = logger
    impt.process_import_schema()
