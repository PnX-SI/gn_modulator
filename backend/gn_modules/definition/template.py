import copy

from gn_modules.utils.cache import get_global_cache
from gn_modules.utils.errors import add_error
from gn_modules.utils.commons import replace_in_dict
import json

import re


class DefinitionTemplates:
    """
    méthode pour gérer le traitement
    - des templates de module
    - des templates de layout
    - etc ....
    """

    @classmethod
    def process_definition_templates(cls):
        """
        procède au traitement des templates pour l'ensemble des définitions
        """

        # pour tous les éléments de ce type
        for defininition_key in get_global_cache(["with_template"]).keys():
            cls.process_definition_template(defininition_key)

    @classmethod
    def process_definition_template(cls, definition_with_template_key):
        """
        traite une definition qui herite d'un template
        """

        # definition qui herite du template
        definition_with_template = cls.get_definition(
            "with_template", definition_with_template_key
        )

        # check reference ??

        # clé du template
        template_name = definition_with_template["with_template"].get("name")

        if not template_name:
            add_error(
                msg="Le champs <template.name> n'est pas défini",
                definition_type="with_template",
                definition_key=definition_with_template_key,
                code="ERR_TEMPLATE_NO_NAME",
            )

        # definition du template
        template = cls.get_definition("template", template_name)

        if template is None:
            add_error(
                msg="Le template {template_name} n'a pas été trouvé",
                definition_type="with_template",
                definition_key=definition_with_template_key,
                code="ERR_TEMPLATE_NOT_FOUND",
            )

        template_params = definition_with_template["with_template"].get("params", {})

        template_defaults = template["template"].get("defaults", {})

        params = copy.deepcopy(template_defaults)
        params.update(template_params)

        processed_definition = copy.deepcopy(template)
        processed_definition.pop("template")

        for param_key, param_item in params.items():
            processed_definition = replace_in_dict(
                processed_definition, f"__{param_key.upper()}__", param_item
            )

        # check s'il reste des ____
        remindings__ = re.findall(r"__(.*?)__", json.dumps(processed_definition))

        if remindings__:
            remindings__str = ", ".join(
                map(lambda x: f"__{x}__", list(dict.fromkeys(remindings__)))
            )
            add_error(
                msg=f"Le ou les champs suivants n'ont pas été résolus : {remindings__str}",
                definition_type="with_template",
                definition_key=definition_with_template_key,
                code="ERR_TEMPLATE_UNRESOLVED_FIELDS",
            )
            return

        cls.save_in_cache_definition(
            processed_definition,
            cls.get_file_path("with_template", definition_with_template_key),
        )

    @classmethod
    def process_module_template(cls, definition, template):
        """
        module qui herite d'un template

        """

        processed_definition = copy.deepcopy(template)
        module_code = definition["module_code"]
        processed_definition["module_code"] = module_code
        processed_definition["module"] = definition["module"]

        processed_definition = replace_in_dict(processed_definition, "M.MODULE_CODE", module_code)

        return processed_definition

    @classmethod
    def process_data_template(cls, definition, template):
        """
        feature qui herite d'un template
        """

        processed_definition = copy.deepcopy(template)
        template_params = processed_definition["template"].get("params", {})
        if template_params.get("module_code"):
            processed_definition = replace_in_dict(
                processed_definition,
                "M.MODULE_CODE",
                template_params.get("module_code"),
            )

        return processed_definition
