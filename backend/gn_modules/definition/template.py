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
    def process_templates(cls):
        """
        procède au traitement des templates pour l'ensemble des définitions
        """

        for definition_type in cls.definition_types():
            for definition_key in cls.definition_codes_for_type(definition_type):
                definition = cls.get_definition(definition_type, definition_key)
                if not definition.get("template_code"):
                    continue
                cls.process_template(definition_type, definition_key)

    @classmethod
    def get_unresolved_params(cls, definition):
        """ """

        unresolved_params = re.findall(r"__(.*?)__", json.dumps(definition))
        return list(dict.fromkeys(unresolved_params))

    @classmethod
    def process_template(cls, definition_type, defininition_key):
        """
        traite une definition qui herite d'un template
        """

        # definition qui herite du template
        definition = cls.get_definition(definition_type, defininition_key)

        # check reference ??

        # clé du template
        template_code = definition["template_code"]

        # definition du template
        template = cls.get_definition(definition_type, template_code)

        if template is None:
            add_error(
                msg=f"Le template {template_code} n'a pas été trouvé",
                definition_type=definition_type,
                definition_code=defininition_key,
                code="ERR_TEMPLATE_NOT_FOUND",
            )

            cls.remove_from_cache(definition_type, defininition_key)
            return

        template_params = definition.get("params", {})

        template_defaults = template.get("defaults", {})

        params = copy.deepcopy(template_defaults)
        params.update(template_params)

        processed_definition = copy.deepcopy(template)

        for param_key, param_item in params.items():
            processed_definition = replace_in_dict(
                processed_definition, f"__{param_key.upper()}__", param_item
            )

        for key in ["title", "code", "description"]:
            processed_definition[key] = definition.get(key)

        # check s'il reste des ____
        unresolved_params = cls.get_unresolved_params(processed_definition)
        if unresolved_params:
            remindings__str = ", ".join(map(lambda x: f"__{x}__", unresolved_params))
            add_error(
                msg=f"Le ou les champs suivants n'ont pas été résolus : {remindings__str}",
                definition_type="use_template",
                definition_code=definition,
                code="ERR_TEMPLATE_UNRESOLVED_FIELDS",
                template_file_path=str(cls.get_file_path("template", template_code)),
            )

            cls.remove_from_cache(definition_type, defininition_key)

            return

        cls.save_in_cache_definition(
            processed_definition,
            cls.get_file_path(definition_type, defininition_key),
            check_existing_definition=False,
        )
