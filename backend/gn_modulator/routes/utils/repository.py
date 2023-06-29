from flask import request, make_response
from gn_modulator import ModuleMethods, SchemaMethods
from .params import parse_request_args
from sqlalchemy import orm


def get_list_rest(module_code, object_code, additional_params={}):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)

    params = {
        **parse_request_args(object_definition),
        **additional_params,
    }

    cruved_type = params.get("cruved_type") or "R"
    query_infos = sm.get_query_infos(
        module_code=module_code,
        cruved_type=cruved_type,
        params=params,
        url=request.url,
    )

    query_list = sm.query_list(module_code=module_code, cruved_type=cruved_type, params=params)

    if params.get("sql"):
        sql_txt = sm.cls.sql_txt(query_list)
        response = make_response(
            sm.cls.format_sql(sql_txt),
            200,
        )
        response.mimetype = "text/plain"
        return response

    res_list = query_list.all()

    out = {
        **query_infos,
        "data": sm.serialize_list(
            res_list,
            fields=params.get("fields"),
            as_geojson=params.get("as_geojson"),
            flat_keys=params.get("flat_keys"),
        ),
    }

    return out


def get_one_rest(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)

    params = parse_request_args(object_definition)

    try:
        m = sm.get_row(
            value,
            field_name=params.get("field_name"),
            module_code=module_code,
            cruved_type="R",
            params=params,
        ).one()

    except sm.errors.SchemaUnsufficientCruvedRigth as e:
        return f"Erreur Cruved : {str(e)}", 403

    except orm.exc.NoResultFound as e:
        return (
            f"Pas de resultats trouvé pour {schema_code} avec ({params.get('field_name') or sm.pk_field_name()})=({value})",
            404,
        )

    return sm.serialize(m, fields=params.get("fields"), as_geojson=params.get("as_geojson"))


def post_rest(module_code, object_code):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)

    data = request.get_json()
    # on verifie les champs
    params = parse_request_args(object_definition)

    try:
        m = sm.insert_row(data, commit=True)

    except sm.errors.SchemaUnsufficientCruvedRigth as e:
        return "Erreur Cruved : {}".format(str(e)), 403

    return sm.serialize(m, fields=params.get("fields"), as_geojson=params.get("as_geojson"))


def patch_rest(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)

    data = request.get_json()
    params = parse_request_args(object_definition)

    authorized_write_fields = ModuleMethods.get_autorized_fields(
        module_code, object_code, write=True
    )

    try:
        m, _ = sm.update_row(
            value,
            data,
            field_name=params.get("field_name"),
            module_code=module_code,
            params=params,
            authorized_write_fields=authorized_write_fields,
            commit=True,
        )

    except sm.errors.SchemaUnsufficientCruvedRigth as e:
        return "Erreur Cruved : {}".format(str(e)), 403
    except Exception as e:
        print(e)
        raise (e)

    return sm.serialize(m, fields=params.get("fields"), as_geojson=params.get("as_geojson"))


def delete_rest(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)

    params = parse_request_args(object_definition)

    m = sm.get_row(
        value,
        field_name=params.get("field_name"),
        module_code=module_code,
        cruved_type="D",
        params=params,
    ).one()
    dict_out = sm.serialize(m, fields=params.get("fields"), as_geojson=params.get("as_geojson"))

    try:
        sm.delete_row(
            value, module_code=module_code, field_name=params.get("field_name"), commit=True
        )

    except sm.errors.SchemaUnsufficientCruvedRigth as e:
        return "Erreur Cruved : {}".format(str(e)), 403

    return dict_out

    pass


def get_page_number_and_list(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)

    params = parse_request_args(object_definition)
    page_number = sm.get_page_number(value, module_code, params.get("cruved_type") or "R", params)

    return get_list_rest(module_code, object_code, additional_params={"page": page_number})
