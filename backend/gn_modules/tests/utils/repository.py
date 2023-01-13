from gn_modules.schema import SchemaMethods


def test_schema_repository(schema_code=None, data=None, data_update=None):
    """
    test pour un cycle get insert update delete
    """

    if schema_code is None:
        return

    sm = SchemaMethods(schema_code)
    fields = list(data.keys()) + [sm.pk_field_name()]
    pk_field_name = sm.pk_field_name()
    label_field_name = sm.label_field_name()

    unique = sm.attr("meta.unique")

    data_search_row = [data[unique_key] for unique_key in unique]

    # 1 test row does not exist
    res_get_row = sm.get_row_as_dict(data_search_row, field_name=unique)
    assert res_get_row is None

    # 2 insert row
    sm.insert_row(data)
    res_get_row = sm.get_row_as_dict(data_search_row, field_name=unique, fields=fields)
    assert res_get_row is not None
    assert res_get_row[label_field_name] == data[label_field_name]

    id = res_get_row[pk_field_name]

    # 3 update_row
    if data_update:
        sm.update_row(id, data_update)
        res_get_row = sm.get_row_as_dict(id, fields=fields)
        assert res_get_row is not None
        assert res_get_row[pk_field_name] == id
        for key in data_update:
            assert data_update[key] == res_get_row[key]

    # 4 delete row
    sm.delete_row(id)
    res_get_row = sm.get_row_as_dict(id, fields=fields)
