"""
    classe pour gérer la configuration des modules
"""

import copy
from flask import g
from gn_modulator.schema import SchemaMethods
from gn_modulator.utils.cache import get_global_cache, set_global_cache
from geonature.core.gn_permissions.tools import cruved_scope_for_user_in_module


class ModulesConfigBase:
    """
    Méthodes pour gérer la configuration des modules
    """

    @classmethod
    def module_config(cls, module_code):
        """
        Retourne la configuration du module référencé par 'module_code'
        """

        module_config = get_global_cache(["module", module_code, "config"])

        if module_config is None:
            raise cls.errors.ModuleNotFoundError(
                "La config du module de code {} n'a pas été trouvée".format(module_code)
            )

        return module_config

    @classmethod
    def init_module_config(cls, module_code):
        """
        Initialise la config d'un module
        """

        module_config = None

        # config depuis les definitions
        module_definition = get_global_cache(["module", module_code, "definition"])

        # config depuis la base (gn_commons.t_module)
        module_db = SchemaMethods("commons.module").get_row_as_dict(
            module_code,
            field_name="module_code",
            fields=[
                "module_code",
                "module_picto",
                "module_desc",
                "module_label",
                "module_path",
            ],
        )

        module_config = copy.deepcopy(module_definition)

        module_config["registred"] = module_db is not None
        if module_config["registred"]:
            for key_config_db in module_db or {}:
                module_config["module"][key_config_db] = module_config["module"].get(
                    key_config_db, module_db[key_config_db]
                )

        # mise en cache
        set_global_cache(["module", module_code, "config"], module_config)

        # process de la config

        # params
        cls.process_module_objects(module_code)

        # - pages

        cls.process_pages(module_code)

        cls.process_tree(module_code)

        if module_config.get("registred"):
            cls.process_module_params(module_code)

        return module_config

    @classmethod
    def modules_config(cls):
        return {module_code: cls.module_config(module_code) for module_code in cls.module_codes()}
