from functools import wraps
from werkzeug.exceptions import Forbidden

from geonature.core.gn_permissions.decorators import check_cruved_scope

from gn_modulator import ModuleMethods, SchemaMethods
from gn_modulator.utils.cache import get_global_cache
from gn_modulator.routes.utils.repository import parse_request_args


def check_fields(module_code, object_code):
    """
    fonction pour vérifier que les champs (fields) utilisé pour une route sont
    bien autorisés
    - pour ne pas avoir un accès aux info de toutes la base
    - pour ne pas modifier des champs que l'on ne souhaite pas modifier
    """

    object_definition = ModuleMethods.object_config(module_code, object_code)

    schema_code = ModuleMethods.schema_code(module_code, object_code)

    params = parse_request_args(object_definition)
    fields = params["fields"]

    sm = SchemaMethods(schema_code)

    # les champs autorisés sont récupérés depuis le cache
    # ils ont été déterminés à l'unitialisation des modules (methode ModuleMethods.process_fields)
    authorized_fields = ModuleMethods.get_autorized_fields(module_code, object_code)

    # liste des champs invalides
    # - cad ne correspondent pas à un champs du schema
    unvalid_fields = sorted(
        list(filter(lambda f: not sm.has_property(f) and f != "scope", fields))
    )

    # liste des champs non autorisés
    # - cad ne font pas parti des champs autorisés
    unauthorized_fields = sorted(list(filter(lambda f: f not in authorized_fields, fields)))

    # retour en cas de champs invalide
    if unvalid_fields:
        return {
            "code": "ERR_REST_API_UNVALID_FIELD",
            "unvalid_fields": unvalid_fields,
            "authorized_fields": authorized_fields,
            "msg": f"Les champs suivants ne sont pas des clé valides: <br>{', '.join(unvalid_fields)}",
        }

    # retour en cas de champs non autorisé
    if unauthorized_fields:
        msg = f"Les champs suivants ne sont pas autorisés pour cette requete {','.join(unauthorized_fields) }"

        return {
            "code": "ERR_REST_API_UNAUTHORIZED_FIELD",
            "unauthorized_fields": unauthorized_fields,
            "authorized_fields": authorized_fields,
            "msg": msg,
        }


def check_module_object_route(action):
    def _check_module_object_route(fn):
        """
        decorateur qui va vérifier si la route est bien définie
        pour un module un object et un action (CRUVED) donnés
        puis effectue check_cruved_scope pour vérifier le droit de l'utilateur à accéder à cette route
        """

        @wraps(fn)
        def __check_module_object_route(*args, **kwargs):
            module_code = kwargs["module_code"]
            object_code = kwargs["object_code"]

            module_config = ModuleMethods.module_config(module_code)

            if not module_config:
                raise Forbidden(description=f"Module {module_code} does not exists")

            if not module_config.get("registred"):
                raise Forbidden(description=f"Module {module_code} is not registred")

            object_config = ModuleMethods.object_config(module_code, object_code)

            if not object_config:
                raise Forbidden(
                    description=f"object {object_code} of module {module_code} is not defined"
                )

            cruved = object_config.get("cruved", "")

            if action not in cruved:
                raise Forbidden(
                    description=f"action {action} is not defined for object {object_code} of module {module_code}"
                )

            # pour les actions d'import on regarde les droit de creation C
            action_cruved = "C" if action == "I" else action

            # verification des champs
            field_errors = check_fields(module_code, object_code)
            if field_errors:
                return field_errors, 403

            return check_cruved_scope(action_cruved, module_code=module_code)(fn)(*args, **kwargs)

        return __check_module_object_route

    return _check_module_object_route
