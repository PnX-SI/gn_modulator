import pathlib

from gn_modulator.utils.env import import_dir


def upload_import_file(module_code, object_code, import_number, file):
    import_dir().mkdir(parents=True, exist_ok=True)

    file_name = f"{import_number}_{module_code}_{object_code}_{file.filename}"
    file_path = pathlib.Path(import_dir() / file_name)
    file.save(str(file_path))

    return file_path
