from functools import wraps
from gn_modulator import ModuleMethods
from geonature.core.gn_permissions.decorators import check_cruved_scope
from werkzeug.exceptions import Forbidden


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

            return check_cruved_scope(action_cruved, module_code=module_code)(fn)(*args, **kwargs)

        return __check_module_object_route

    return _check_module_object_route
