import json, yaml
import logging
from flask import request, jsonify

from sqlalchemy import orm, select
from gn_modulator.routes.utils.decorators import check_module_object_route
from geonature.utils.env import db
from geonature.core.gn_permissions import decorators as permissions
from gn_modulator.blueprint import blueprint
from gn_modulator.module import ModuleMethods

from gn_modulator.imports.files import upload_import_file
from gn_modulator.imports.models import TImport
from gn_modulator.tasks import process_import
from gn_modulator import SchemaMethods

log = logging.getLogger()


@permissions.check_cruved_scope("R", module_code="MODULATOR", object_code="ADMIN")
@blueprint.route("import_feature", methods=["POST"])
def api_admin_import_feature():
    feature_data = request.get_json()

    out = ""
    if isinstance(feature_data, dict):
        res = SchemaMethods.process_data_item(feature_data)
        out += SchemaMethods.txt_data_info(res)

    if isinstance(feature_data, list):
        for fd in feature_data:
            res = SchemaMethods.process_data_item(fd)
            out += SchemaMethods.txt_data_info(res)

    return {"msg": out}, 200


@check_module_object_route("I")  # object import ??
@blueprint.route("import_async/<module_code>/<object_code>/<id_import>", methods=["POST"])
@blueprint.route(
    "import_async/<module_code>/<object_code>/", methods=["POST"], defaults={"id_import": None}
)
def api_import_async(module_code, object_code, id_import):
    return f_api_import_async(module_code, object_code, id_import)


@blueprint.route("import_async_admin/<module_code>/<object_code>/<id_import>", methods=["POST"])
@blueprint.route(
    "import_async_admin/<module_code>/<object_code>/",
    methods=["POST"],
    defaults={"id_import": None},
)
def api_import_async_admin(module_code, object_code, id_import):
    return f_api_import_async(module_code, object_code, id_import)


def f_api_import_async(module_code, object_code, id_import):
    """_summary_"""

    sm = SchemaMethods("modules.import")

    options = json.loads(request.form.get("options")) if request.form.get("options") else {}

    if id_import:
        try:
            impt = db.session.execute(select(TImport).filter_by(id_import=id_import)).scalar_one()
        except orm.exc.NoResultFound:
            return f"Pas d'import trouvé pour id_import={id_import}", 404
    else:
        impt = TImport(module_code=module_code, object_code=object_code, options=options)
        db.session.add(impt)
        impt.status = "STARTING"
        db.session.commit()

    # condition import statut
    if not impt.data_file_path:
        files_path = {}
        if request.files:
            for file_key in request.files:
                file = request.files.get(file_key)
                files_path[file_key] = upload_import_file(
                    module_code, object_code, impt.id_import, file
                )

        impt.data_file_path = files_path.get("data_file") and str(files_path.get("data_file"))

    # test status ?
    if impt.status not in ["STARTING", "PENDING"]:
        return f"Erreur process import status : {impt.status}", 500
    # db.session.commit()
    sig = process_import.s(impt.id_import)
    task = sig.freeze()
    impt.task_id = task.task_id
    db.session.commit()
    sig.delay()

    return sm.serialize(
        impt,
        fields=[
            "id_import",
            "schema_code",
            "module_code",
            "object_code",
            "id_digitiser",
            "data_type",
            "csv_delimiter",
            "res",
            "errors",
            "options",
            "tables",
            "status",
            "steps",
        ],
    )
