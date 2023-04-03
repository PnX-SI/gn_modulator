from gn_modulator import DefinitionMethods, ModuleMethods, SchemaMethods
from gn_modulator.blueprint import blueprint
from .utils.decorators import check_module_object_route
from .utils.params import parse_request_args


@blueprint.route("/exports/<module_code>/<object_code>/<export_code>", methods=["GET"])
@check_module_object_route("E")
def api_export(module_code, object_code, export_code):
    """
    Route pour les exports
    """

    # récupération de la configuration de l'export
    export_definition = DefinitionMethods.get_definition("export", export_code)

    object_definition = ModuleMethods.object_config(module_code, object_code)
    schema_code = ModuleMethods.schema_code(module_code, object_code)
    # renvoie une erreur si l'export n'est pas trouvé
    if export_definition is None:
        return "L'export correspondant au code {export_code} n'existe pas", 403

    # definitions des paramètres

    # - query params + object_definition
    params = parse_request_args(object_definition)

    # - export_definition
    #  - on force fields a être
    #   - TODO faire l'intersection de params['fields'] et export_definition['fields'] (si params['fields'] est défini)
    params["fields"] = export_definition["fields"]
    #   - TODO autres paramètres ????

    params["process_field_name"] = export_definition.get("process_field_name")
    params["process_label"] = export_definition.get("process_label")

    cruved_type = params.get("cruved_type") or "R"

    # recupération de la liste
    sm = SchemaMethods(schema_code)

    query_list = sm.query_list(module_code=module_code, cruved_type=cruved_type, params=params)

    # on assume qu'il n'y que des export csv
    # TODO ajouter query param export_type (csv, shape, geosjon, etc) et traiter les différents cas
    return sm.process_export_csv(module_code, query_list, params)
