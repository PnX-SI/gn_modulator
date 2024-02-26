from flask import request, make_response, g
from gn_modulator import ModuleMethods, SchemaMethods
from .params import parse_request_args
from sqlalchemy import orm
from gn_modulator.query.utils import pretty_sql
from gn_modulator.query.repository import query_list
from geonature.core.gn_permissions.tools import has_any_permissions
from geonature.utils.env import db


def get_list_rest(module_code, object_code, additional_params={}):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)

    id_role = g.current_user.id_role

    # on peut redéfinir le module_code pour le choix des droits
    permission_module_code = object_definition.get("module_code", module_code)
    params = {**parse_request_args(object_definition), **additional_params}

    action = params.get("action") or "R"
    query_infos = (
        {}
        if params.get("no_info")
        else sm.get_query_infos(
            module_code=permission_module_code,
            action=action,
            params=params,
            url=request.url,
            id_role=id_role,
        )
    )

    q_list = query_list(
        sm.Model(),
        module_code=permission_module_code,
        action=action,
        params=params,
        query_type="select",
        id_role=id_role,
    )

    if params.get("sql"):
        # test si droit admin
        if not has_any_permissions("R", id_role, "MODULATOR", "ADMIN"):
            return (
                "Vous n'avez pas les droit pour effectuer des actions d'admin pour le module MODULATOR",
                403,
            )
        response = make_response(
            pretty_sql(q_list),
            200,
        )
        response.mimetype = "text/plain"
        return response

    res_list = [] if params.get("only_info") else q_list.all()

    out = {
        **query_infos,
        "data": sm.serialize_list(
            res_list,
            fields=params.get("fields"),
            as_geojson=params.get("as_geojson"),
            flat_keys=params.get("flat_keys"),
        ),
    }

    if params.get("no_info"):
        return out["data"]

    return out


def get_one_rest(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)
    id_role = g.current_user.id_role
    params = parse_request_args(object_definition)

    permission_module_code = object_definition.get("module_code", module_code)

    try:
        q = sm.get_row(
            value,
            field_name=params.get("field_name"),
            module_code=permission_module_code,
            action="R",
            params=params,
            id_role=id_role,
        )

        m = q.one()
    except sm.errors.SchemaUnsufficientCruvedRigth as e:
        return f"Erreur Cruved : {str(e)}", 403

    except orm.exc.NoResultFound as e:
        return (
            f"Pas de resultats trouvé pour {schema_code} avec ({params.get('field_name') or sm.Model().pk_field_name()})=({value})",
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
        return f"Erreur Cruved : {str(e)}", 403

    return sm.serialize(m, fields=params.get("fields"), as_geojson=params.get("as_geojson"))


def patch_rest(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)
    id_role = g.current_user.id_role

    permission_module_code = object_definition.get("module_code", module_code)

    data = request.get_json()
    params = parse_request_args(object_definition)

    authorized_write_fields = ModuleMethods.get_autorized_fields(module_code, object_code, "write")

    try:
        m, _ = sm.update_row(
            value,
            data,
            field_name=params.get("field_name"),
            module_code=permission_module_code,
            params=params,
            authorized_write_fields=authorized_write_fields,
            commit=True,
            id_role=id_role,
        )

    except sm.errors.SchemaUnsufficientCruvedRigth as e:
        return f"Erreur Cruved : {str(e)}", 403
    except Exception as e:
        raise (e)

    return sm.serialize(m, fields=params.get("fields"), as_geojson=params.get("as_geojson"))


def delete_rest(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)
    id_role = g.current_user.id_role

    permission_module_code = object_definition.get("module_code", module_code)

    params = parse_request_args(object_definition)

    dict_out = sm.get_row_as_dict(
        value,
        field_name=params.get("field_name"),
        module_code=permission_module_code,
        action="D",
        fields=params.get("fields"),
    )

    try:
        sm.delete_row(
            value,
            module_code=module_code,
            field_name=params.get("field_name"),
            commit=True,
            id_role=id_role,
        )

    except sm.errors.SchemaUnsufficientCruvedRigth as e:
        return f"Erreur Cruved : {str(e)}", 403

    return dict_out


def get_page_number_and_list(module_code, object_code, value):
    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    sm = SchemaMethods(schema_code)
    id_role = g.current_user.id_role
    permission_module_code = object_definition.get("module_code", module_code)

    params = parse_request_args(object_definition)
    page_number = sm.get_page_number(
        value,
        permission_module_code,
        params.get("action") or "R",
        params,
        id_role=id_role,
    )

    return get_list_rest(module_code, object_code, additional_params={"page": page_number})
