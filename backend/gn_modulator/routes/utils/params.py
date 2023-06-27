import json
from flask import request
from gn_modulator.utils.filters import parse_filters


def parse_request_args(object_definition={}):
    params = {
        "as_geojson": load_param(request.args.get("as_geojson", "false")),
        "flat_keys": load_param(request.args.get("flat_keys", "false")),
        "compress": load_param(request.args.get("compress", "false")),
        "fields": load_array_param(request.args.get("fields")),
        "field_name": load_param(request.args.get("field_name", "null")),
        "filters": parse_filters(request.args.get("filters")),
        "prefilters": parse_filters(request.args.get("prefilters")),
        "page": load_param(request.args.get("page", "null")),
        "page_size": load_param(request.args.get("page_size", "null")),
        "sort": load_array_param(request.args.get("sort")),
        "value": load_param(request.args.get("value", "null")),
        "as_csv": load_param(request.args.get("as_csv", "false")),
        "cruved_type": load_param(request.args.get("cruved_type", "null")),
        "sql": "sql" in request.args,
        "test": load_param(request.args.get("test", "null")),
    }

    if "prefilters" in object_definition:
        params["prefilters"] = (
            parse_filters(object_definition["prefilters"]) + params["prefilters"]
        )

    return params


def load_array_param(param):
    """
    pour les cas ou params est une chaine de caractère séparée par des ','
    """

    if not param:
        return []

    return list(map(lambda x: x.strip(), param.split(",")))


def load_param(param):
    if param == "undefined":
        return None

    # pour traiter les true false
    try:
        return json.loads(param)
    except Exception:
        return param
