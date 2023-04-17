import json
from flask import request, jsonify

from sqlalchemy import orm
from gn_modulator.routes.utils.decorators import check_module_object_route
from geonature.utils.env import db

from gn_modulator.blueprint import blueprint
from gn_modulator.module import ModuleMethods

from gn_modulator.imports.files import upload_import_file
from gn_modulator.imports.models import TImport


@check_module_object_route("I")  # object import ??
@blueprint.route("import/<module_code>/<object_code>/<id_import>", methods=["POST"])
@blueprint.route(
    "import/<module_code>/<object_code>/", methods=["POST"], defaults={"id_import": None}
)
def api_import(module_code, object_code, id_import):
    options = json.loads(request.form.get("options")) if request.form.get("options") else {}

    if id_import:
        try:
            impt = TImport.query.filter_by(id_import=id_import).one()
        except orm.exc.NoResultFound:
            return f"Pas d'import trouvé pour id_import={id_import}", 404
    else:
        impt = TImport(module_code, object_code, options=options)
        db.session.add(impt)
        db.session.flush()

    if not impt.status:
        files_path = {}
        if request.files:
            for file_key in request.files:
                file = request.files.get(file_key)
                files_path[file_key] = upload_import_file(
                    module_code, object_code, impt.id_import, file
                )

        impt.data_file_path = files_path.get("data_file") and str(files_path.get("data_file"))

    impt.process_import_schema()

    out = impt.as_dict()
    db.session.commit()
    return out
