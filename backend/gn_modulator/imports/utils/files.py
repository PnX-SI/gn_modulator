import pathlib
from geonature.core.gn_commons.file_manager import upload_file
from gn_modulator.utils.env import IMPORT_DIR


def upload_import_file(module_code, object_code, import_number, file):
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)

    file_name = f"{import_number}_{module_code}_{object_code}_{file.name}"
    return pathlib.Path(upload_file(file, IMPORT_DIR, file_name))
