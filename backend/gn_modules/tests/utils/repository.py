from gn_modules.schema import SchemaMethods


def test_schema_repository(schema_code=None, data=None):
    """
    test pour un cycle get insert update delete
    """

    if schema_code is None:
        return

    sm = SchemaMethods(schema_code)

    unique = sm.attr("meta.unique")

    data_search_row = [data[unique_key] for unique_key in unique]

    res_get_row = sm.get_row_as_dict(data_search_row, field_name=unique)

    assert res_get_row is None
