import copy

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
    def check_template_definitions(cls):
        """
        verifie les template et use_template
        """

        for definition_type in ["template", "use_template"]:
            for defininition_code in cls.definition_codes_for_type(definition_type):
                cls.local_check_definition(definition_type, defininition_code)

    @classmethod
    def process_templates(cls):
        """
        procède au traitement des templates pour l'ensemble des définitions
        """

        for defininition_key in cls.definition_codes_for_type("use_template"):
            cls.process_template(defininition_key)

    @classmethod
    def process_template(cls, definition_use_template_code):
        """
        traite une definition qui herite d'un template
        """

        # definition qui herite du template
        definition_use_template = cls.get_definition("use_template", definition_use_template_code)

        # check reference ??

        # clé du template
        template_code = definition_use_template["template_code"]

        # definition du template
        template = cls.get_definition("template", template_code)

        if template is None:
            add_error(
                msg=f"Le template {template_code} n'a pas été trouvé",
                definition_type="use_template",
                definition_code=definition_use_template_code,
                code="ERR_TEMPLATE_NOT_FOUND",
            )

            cls.remove_from_cache("use_template", definition_use_template_code)
            return

        # check code template et use_template
        template_type = template["template"]["type"]
        if definition_use_template["code"].split(".")[-1] != template_type:
            add_error(
                msg=f"Le code de use_template {definition_use_template['code']} devrait se terminer par '.{template_type}'",
                definition_type="use_template",
                definition_code=definition_use_template_code,
                code="ERR_USE_TEMPLATE_CODE",
            )
            cls.remove_from_cache("use_template", definition_use_template_code)
            return

        template_params = definition_use_template.get("params", {})

        template_defaults = template.get("defaults", {})

        params = copy.deepcopy(template_defaults)
        params.update(template_params)

        processed_definition = copy.deepcopy(template["template"])
        processed_definition["use_template"] = True

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
                definition_type="use_template",
                definition_code=definition_use_template_code,
                code="ERR_TEMPLATE_UNRESOLVED_FIELDS",
                template_file_path=str(cls.get_file_path("template", template_code)),
            )

            cls.remove_from_cache("use_template", definition_use_template_code)

            return

        cls.save_in_cache_definition(
            processed_definition,
            cls.get_file_path("use_template", definition_use_template_code),
        )
