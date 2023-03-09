from gn_modulator.imports.models import TImport
from gn_modulator.utils.commons import getAttr
from geonature.utils.env import db


def test_data_file(
    schema_code=None, data_file_path=None, mapping_file_path=None, expected_infos={}
):
    if not (schema_code and data_file_path):
        return

    with db.session.begin_nested():
        # ici _insert_data est à true pour intégrer les avec un insert
        # et non un copy qui ne marche pas en test
        impt = TImport(
            schema_code=schema_code,
            data_file_path=data_file_path,
            mapping_file_path=mapping_file_path,
            _insert_data=True,
        )
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


def test_import_code(import_code=None, data_dir_path=None, expected_infos=[]):
    if not (import_code and data_dir_path):
        return

    imports = TImport.process_import_code(import_code, data_dir_path, commit=False)
    assert len(imports) > 0

    for impt in imports:
        assert len(impt.errors) == 0

    for index, expected_info in enumerate(expected_infos):
        impt = imports[index]
        import_infos = impt.as_dict()
        for key in expected_info:
            txt_err = f"schema_code: {impt.schema_code}, key: {key},  expected: {expected_info.get(key)}, import: {getAttr(import_infos, key)}"
            assert getAttr(import_infos, key) == expected_info.get(key), txt_err
