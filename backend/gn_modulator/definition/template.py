import copy

from gn_modulator.utils.errors import add_error
from gn_modulator.utils.commons import replace_in_dict
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
    def get_unresolved_template_params(cls, definition):
        """ """

        unresolved_template_params = re.findall(r"__(.*?)__", json.dumps(definition))
        unresolved_template_params = list(dict.fromkeys(unresolved_template_params))
        if "f" in unresolved_template_params:
            unresolved_template_params.remove("f")
        return list(dict.fromkeys(unresolved_template_params))

    @classmethod
    def process_template(cls, definition_type, defininition_code):
        """
        traite une definition qui herite d'un template
        """

        # definition qui herite du template
        definition = cls.get_definition(definition_type, defininition_code)

        # check reference ??

        # clé du template
        template_code = definition["template_code"]

        # definition du template
        template = cls.get_definition(definition_type, template_code)

        if template is None:
            add_error(
                msg=f"Le template {template_code} n'a pas été trouvé",
                definition_type=definition_type,
                definition_code=defininition_code,
                code="ERR_TEMPLATE_NOT_FOUND",
            )

            cls.remove_from_cache(definition_type, defininition_code)
            return

        template_params = definition.get("template_params", {})

        template_defaults = template.get("template_defaults", {})

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
        unresolved_template_params = cls.get_unresolved_template_params(processed_definition)
        if unresolved_template_params:
            remindings__str = ", ".join(map(lambda x: f"__{x}__", unresolved_template_params))
            add_error(
                msg=f"Le ou les champs suivants n'ont pas été résolus : {remindings__str}",
                definition_type=processed_definition["type"],
                definition_code=processed_definition["code"],
                code="ERR_TEMPLATE_UNRESOLVED_FIELDS",
                template_file_path=str(cls.get_file_path("template", template_code)),
            )

            cls.remove_from_cache(definition_type, defininition_code)

            return

        cls.save_in_cache_definition(
            processed_definition,
            cls.get_file_path(definition_type, defininition_code),
            check_existing_definition=False,
        )
