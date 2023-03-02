import pathlib
from flask import request, jsonify
from gn_modulator.schema import SchemaMethods
from gn_modulator.module import ModuleMethods
from gn_modulator.utils.env import IMPORT_DIR
from geonature.core.gn_commons.file_manager import upload_file, remove_file, rename_file


class ImportApi:
    @classmethod
    def upload_file(cls, module_code, object_code, import_number, file):
        IMPORT_DIR.mkdir(parents=True, exist_ok=True)

        file_name = f"{import_number}_{file.name}"
        return pathlib.Path(upload_file(file, IMPORT_DIR, file_name))

    @classmethod
    def process_api_import(cls, module_code):
        import_number = SchemaMethods.generate_import_number()

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

        files_path = {}
        if request.files:
            for file_key in request.files:
                file = request.files.get(file_key)
                files_path[file_key] = cls.upload_file(
                    module_code, object_code, import_number, file
                )
        data_file_path = files_path.get("data_file")

        if not (data_file_path):
            return {
                "errors": [
                    {
                        "msg": "Il n'y a pas de fichier de données",
                        "code": "ERR_IMPORT_NO_DATA_FILE",
                    }
                ]
            }

        import_number = SchemaMethods.process_import_schema(
            schema_code, data_file_path, import_number=import_number, commit=True
        )
        import_infos = SchemaMethods.import_get_infos(import_number, schema_code)
        print(SchemaMethods.import_pretty_infos(import_number, schema_code))  # __DEBUG

        import_infos.pop("data_file_path", None)

        return jsonify(import_infos)
