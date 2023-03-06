from flask import request, jsonify

from geonature.core.gn_permissions.decorators import check_cruved_scope
from geonature.utils.env import db

from gn_modulator.blueprint import blueprint
from gn_modulator.schema import SchemaMethods
from gn_modulator.module import ModuleMethods


from .utils.files import upload_import_file
from .models import TImport


@check_cruved_scope("R")  # object import ??
@blueprint.route("import/<module_code>", methods=["POST"])
def api_import(module_code):
    object_code = None
    if request.form:
        object_code = request.form.get("object_code")

    schema_code = ModuleMethods.schema_code(module_code, object_code)

    if not schema_code:
        return {
            "errors": [
                {
                    "msg": f"Il n'y pas de schema pour module_code={module_code} et object_code={object_code}",
                    "code": "ERR_IMPORT_SCHEMA_CODE",
                }
            ]
        }

    impt = TImport(schema_code=schema_code)
    db.session.add(impt)

    files_path = {}
    if request.files:
        for file_key in request.files:
            file = request.files.get(file_key)
            files_path[file_key] = upload_import_file(
                module_code, object_code, impt.id_import, file
            )

    impt.data_file_path = str(files_path.get("data_file"))
    db.session.flush()

    impt.process_import_schema()
    print(impt.pretty_infos())

    db.session.commit()

    return impt.as_dict()
