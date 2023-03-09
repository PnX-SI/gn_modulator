from gn_modulator.imports.models import TImport
from gn_modulator.utils.commons import getAttr
from geonature.utils.env import db


def test_data_file(
    schema_code=None, data_file_path=None, mapping_file_path=None, expected_infos={}
):
    if not (schema_code and data_file_path):
        return

    with db.session.begin_nested():
        impt = TImport(schema_code=schema_code, data_file_path=data_file_path, mapping_file_path=mapping_file_path, _insert=True)
        db.session.add(impt)
    assert impt.id_import is not None

    impt.process_import_schema()

    import_infos = impt.as_dict()

    errors = expected_infos.pop("errors", [])

    if len(errors) == 0:
        assert len(import_infos["errors"]) == 0, import_infos["errors"]
    else:
        assert len(errors) == len(import_infos("error"))
        for error in errors:
            assert len([e for e in import_infos["errors"] if error["code"] == e["code"]]) > 0

    for key in expected_infos:
        txt_err = f"schema_code: {schema_code}, key: {key},  expected: {expected_infos.get(key)}, import: {getAttr(import_infos, key)}"
        assert getAttr(import_infos, key) == expected_infos.get(key), txt_err

    return import_infos
