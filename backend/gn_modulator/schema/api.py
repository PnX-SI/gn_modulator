"""
    SchemaMethods : api
"""

import json
from flask.views import MethodView
from flask import request, make_response
from geonature.core.gn_permissions import decorators as permissions
from gn_modulator.utils.cache import get_global_cache, set_global_cache

# from geonature.utils.config import config
from gn_modulator import MODULE_CODE
from gn_modulator.definition import DefinitionMethods
import sqlparse


class SchemaApi:
    """
    class for schema api processing

    doc:
      - https://flask.palletsprojects.com/en/2.0.x/views/

    """

    def method_view_name(self, module_code, object_code, view_type):
        object_code_undot = object_code.replace(".", "_")
        return f"MV_{module_code}_{object_code_undot}_{view_type}"

    def view_name(self, module_code, object_code, view_type):
        """ """
        object_code_undot = object_code.replace(".", "_")
        return f"MV_{module_code}_{object_code_undot}_{view_type}"

    @classmethod
    def base_url(cls):
        """
        base url (may differ with apps (GN, UH, TH, ...))

        TODO process apps ?

        """
        from geonature.utils.config import config

        return "{}/{}".format(config["API_ENDPOINT"], MODULE_CODE.lower())

    def url(self, post_url, full_url=False):
        """
        /{schema_code}{post_url}

        - full/url renvoie l'url complet

        TODO gérer par type d'url ?
        """

        url = self.attr("meta.url", "/{}{}".format(self.schema_code(), post_url))

        if full_url:
            url = "{}{}".format(self.cls.base_url(), url)

        return url

    def parse_request_args(self, request, object_definition={}):
        """
        TODO !!! à refaire avec repo get_list
        parse request flask element
        - filters
        - prefilters
        - fields
        - field_name
        - sort
        - page
        - page_size

        TODO plusieurs possibilités pour le parametrage
        - par exemple au format tabulator ou autre ....
        """

        # params = json.loads(params_txt)
        params = {
            "as_geojson": self.load_param(request.args.get("as_geojson", "false")),
            "flat_keys": self.load_param(request.args.get("flat_keys", "false")),
            "compress": self.load_param(request.args.get("compress", "false")),
            "fields": self.load_array_param(request.args.get("fields")),
            "field_name": self.load_param(request.args.get("field_name", "null")),
            "filters": self.parse_filters(request.args.get("filters")),
            "prefilters": self.parse_filters(request.args.get("prefilters")),
            "page": self.load_param(request.args.get("page", "null")),
            "page_size": self.load_param(request.args.get("page_size", "null")),
            "sort": self.load_array_param(request.args.get("sort")),
            "value": self.load_param(request.args.get("value", "null")),
            "as_csv": self.load_param(request.args.get("as_csv", "false")),
            "cruved_type": self.load_param(request.args.get("cruved_type", "null")),
            "sql": self.load_param(request.args.get("sql", "null")),
            "test": self.load_param(request.args.get("test", "null")),
        }

        if "prefilters" in object_definition:
            params["prefilters"] = (
                self.parse_filters(object_definition["prefilters"]) + params["prefilters"]
            )

        return params

    def load_array_param(self, param):
        """
        pour les cas ou params est une chaine de caractère séparée par des ','
        """

        if not param:
            return []

        return param.split(",")

    def load_param(self, param):
        if param == "undefined":
            return None

        # pour traiter les true false
        try:
            return json.loads(param)
        except Exception:
            return param

    def schema_api_dict(self, module_code, object_definition):
        """
        object_definition : dict
            - prefilters
        """

        def check_fields(fields, write=False):
            authorized_fields = sorted(
                get_global_cache(
                    [
                        "keys",
                        module_code,
                        object_definition["object_code"],
                        "write" if write else "read",
                    ]
                )
                or []
            )

            for elem in [
                self.pk_field_name(),
                self.label_field_name(),
                self.title_field_name(),
                "ownership",
            ]:
                if elem is not None and elem not in authorized_fields:
                    authorized_fields.append(elem)

            unvalid_fields = sorted(
                list(filter(lambda f: not self.has_property(f) and f != "ownership", fields))
            )
            unauthorized_fields = sorted(
                list(filter(lambda f: f not in authorized_fields, fields))
            )

            if unvalid_fields:
                return f"Les champs suivants ne sont pas des clé valides: <br>{', '.join(unvalid_fields)}"

            if unauthorized_fields:
                return f"""
                Les champs suivants ne sont pas authorisé pour cette requete: 
                <br><br>
                - {'<br>- '.join(unauthorized_fields) } 
                <br><br>
                Champs autorisés
                <br><br>
                - {'<br>- '.join(authorized_fields) } 
                """

        def get_rest(self_mv, value=None):
            if value:
                try:
                    return get_one_rest(value)
                except self.errors.SchemaUnsufficientCruvedRigth:
                    return f"Vous n'avez pas les droits suffisants pour accéder à cette requête (schema_code: {self.schema_code()}, module_code: {module_code})"

            else:
                return get_list_rest()

        def get_one_rest(value):
            params = self.parse_request_args(request, object_definition)
            field_errors = check_fields(params["fields"])
            if field_errors:
                return field_errors, 403
            try:
                m = self.get_row(
                    value,
                    field_name=params.get("field_name"),
                    module_code=module_code,
                    cruved_type="R",
                    params=params,
                ).one()

            except self.errors.SchemaUnsufficientCruvedRigth as e:
                return "Erreur Cruved : {}".format(str(e)), 403

            return self.serialize(
                m, fields=params.get("fields"), as_geojson=params.get("as_geojson")
            )

        def get_list_rest(additional_params={}):
            params = {
                **self.parse_request_args(request, object_definition),
                **additional_params,
            }

            field_errors = check_fields(params["fields"])
            if field_errors:
                return field_errors, 403

            cruved_type = params.get("cruved_type") or "R"
            query_infos = self.get_query_infos(
                module_code=module_code,
                cruved_type=cruved_type,
                params=params,
                url=request.url,
            )

            query_list = self.query_list(
                module_code=module_code, cruved_type=cruved_type, params=params
            )

            if params.get("sql"):
                response = make_response(
                    sqlparse.format(str(query_list), reindent=True, keywordcase="upper"),
                    200,
                )
                response.mimetype = "text/plain"
                return response

            res_list = query_list.all()

            out = {
                **query_infos,
                "data": self.serialize_list(
                    res_list,
                    fields=params.get("fields"),
                    as_geojson=params.get("as_geojson"),
                    flat_keys=params.get("flat_keys"),
                ),
            }

            return out

        def post_rest(self_mv):
            params = self.parse_request_args(request, object_definition)
            field_errors = check_fields(params["fields"])
            if field_errors:
                return field_errors, 403

            data = request.get_json()

            try:
                m = self.insert_row(data)

            except self.errors.SchemaUnsufficientCruvedRigth as e:
                return "Erreur Cruved : {}".format(str(e)), 403

            return self.serialize(
                m, fields=params.get("fields"), as_geojson=params.get("as_geojson")
            )

        def patch_rest(self_mv, value):
            params = self.parse_request_args(request, object_definition)
            field_errors = check_fields(params["fields"])
            if field_errors:
                return field_errors, 403

            data = request.get_json()

            # check data fields

            try:
                m, _ = self.update_row(
                    value,
                    data,
                    field_name=params.get("field_name"),
                    module_code=module_code,
                    params=params,
                )

            except self.errors.SchemaUnsufficientCruvedRigth as e:
                return "Erreur Cruved : {}".format(str(e)), 403

            return self.serialize(
                m, fields=params.get("fields"), as_geojson=params.get("as_geojson")
            )

        def delete_rest(self_mv, value):
            params = self.parse_request_args(request, object_definition)

            m = self.get_row(
                value,
                field_name=params.get("field_name"),
                module_code=module_code,
                cruved_type="D",
                params=params,
            ).one()
            dict_out = self.serialize(
                m, fields=params.get("fields"), as_geojson=params.get("as_geojson")
            )

            try:
                self.delete_row(value, field_name=params.get("field_name"))

            except self.errors.SchemaUnsufficientCruvedRigth as e:
                return "Erreur Cruved : {}".format(str(e)), 403

            return dict_out

        def get_page_number(self_mv, value):
            """ """

            params = self.parse_request_args(request, object_definition)
            page_number = self.get_page_number(
                value, module_code, params.get("cruved_type") or "R", params
            )

            return get_list_rest(additional_params={"page": page_number})
            # return {
            # "page": self.get_page_number(
            # value, module_code, params.get("cruved_type") or "R", params
            # )
            # }

        def get_export(self_mv, export_code):
            """
            methode pour gérer la route d'export
                - récupération de la configuration de l'export
            """

            # récupération de la configuration de l'export
            export_definition = DefinitionMethods.get_definition("export", export_code)

            # renvoie une erreur si l'export n'est pas trouvé
            if export_definition is None:
                return "L'export correspondant au code {export_code} n'existe pas", 403

            # definitions des paramètres

            # - query params + object_definition
            params = self.parse_request_args(request, object_definition)

            # - export_definition
            #  - on force fields a être
            #   - TODO faire l'intersection de params['fields'] et export_definition['fields'] (si params['fields'] est défini)
            params["fields"] = export_definition["fields"]
            #   - TODO autres paramètres ????

            cruved_type = params.get("cruved_type") or "R"

            # recupération de la liste
            query_list = self.query_list(
                module_code=module_code, cruved_type=cruved_type, params=params
            )

            # on assume qu'il n'y que des export csv
            # TODO ajouter query param export_type (csv, shape, geosjon, etc) et traiter les différents cas
            return self.process_export_csv(query_list, params)

        return {
            "rest": {
                "get": permissions.check_cruved_scope("R", module_code=module_code)(get_rest),
                "post": permissions.check_cruved_scope("C", module_code=module_code)(post_rest),
                "patch": permissions.check_cruved_scope("U", module_code=module_code)(patch_rest),
                "delete": permissions.check_cruved_scope("D", module_code=module_code)(
                    delete_rest
                ),
            },
            "export": {
                "get": permissions.check_cruved_scope("E", module_code=module_code)(get_export)
            },
            "page_number": {
                "get": permissions.check_cruved_scope("R", module_code=module_code)(
                    get_page_number
                )
            },
        }

    def schema_view_func(self, view_type, module_code, object_definition):
        """
        c'est ici que ce gère le CRUVED pour l'accès aux routes
        """

        schema_api_dict = self.schema_api_dict(module_code, object_definition)[view_type]

        MV = type(
            self.method_view_name(module_code, object_definition["object_code"], view_type),
            (MethodView,),
            schema_api_dict,
        )
        return MV.as_view(self.view_name(module_code, object_definition["object_code"], view_type))

    def register_api(self, bp, module_code, object_code, object_definition={}):
        """
        Fonction qui enregistre une api pour un schema

        TODO s
            -comment gérer la config pour limiter les routes selon le cruved
        """

        cruved = object_definition.get("cruved", "")

        # rest api
        view_func_rest = self.schema_view_func("rest", module_code, object_definition)
        view_func_page_number = self.schema_view_func(
            "page_number", module_code, object_definition
        )
        view_func_export = self.schema_view_func("export", module_code, object_definition)

        # read: GET (liste et one_row)
        if "R" in cruved:
            bp.add_url_rule(
                f"/{object_code}/",
                defaults={"value": None},
                view_func=view_func_rest,
                methods=["GET"],
            )
            bp.add_url_rule(f"/{object_code}/<value>", view_func=view_func_rest, methods=["GET"])
            bp.add_url_rule(
                f"/{object_code}/page_number/<value>",
                view_func=view_func_page_number,
                methods=["GET"],
            )

        # create : POST
        if "C" in cruved:
            bp.add_url_rule(f"/{object_code}/", view_func=view_func_rest, methods=["POST"])

        # update : PATCH
        if "U" in cruved:
            bp.add_url_rule(f"/{object_code}/<value>", view_func=view_func_rest, methods=["PATCH"])

        # delete : DELETE
        if "D" in cruved:
            bp.add_url_rule(
                f"/{object_code}/<value>", view_func=view_func_rest, methods=["DELETE"]
            )

        # export
        if "E" in cruved:  # and object_definition.get("exports"):
            bp.add_url_rule(
                f"/{object_code}/exports/<export_code>",
                view_func=view_func_export,
                methods=["GET"],
            )