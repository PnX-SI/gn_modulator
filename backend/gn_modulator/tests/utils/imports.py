from gn_modulator.schema import SchemaMethods
from gn_modulator.utils.commons import getAttr


def test_data_file(
    schema_code=None, data_file_path=None, pre_process_file_path=None, expected_infos={}
):
    if not (schema_code and data_file_path):
        return

    import_number = SchemaMethods.process_import_schema(
        schema_code,
        data_file_path,
        pre_process_file_path=pre_process_file_path,
        verbose=1,
        insert=True,
    )

    import_infos = SchemaMethods.import_get_infos(import_number, schema_code)

    print(
        {
            "nb_data": import_infos.get("nb_data"),
            "nb_insert": import_infos.get("nb_insert"),
            "nb_update": import_infos.get("nb_update"),
            "errors:": import_infos.get("errors"),
        }
    )

    errors = expected_infos.pop("errors", [])

    if len(errors) == 0:
        assert len(import_infos["errors"]) == 0
    else:
        assert len(errors) == len(import_infos("error"))
        for error in errors:
            assert len([e for e in import_infos["errors"] if error["code"] == e["code"]]) > 0

    for key in expected_infos:
        txt_err = f"schema_code: {schema_code}, key: {key},  expected: {expected_infos.get(key)}, import: {getAttr(import_infos, key)}"
        print(txt_err)
        assert getAttr(import_infos, key) == expected_infos.get(key), txt_err

    return import_infos
