import copy

from gn_modules.utils.cache import get_global_cache, set_global_cache
from gn_modules.utils.commons import replace_in_dict


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

        process_definition_templates_errors = []

        # pour les modules
        for module_code in cls.module_codes():
            process_definition_templates_errors += cls.process_module_template(module_code)

        return process_definition_templates_errors

    @classmethod
    def process_module_template(cls, module_code):
        """
        procède au traitement des templates de module
        """

        process_module_template_errors = []

        definition = get_global_cache(["module", module_code, "definition"])

        template_name = definition.get("module_template")
        if template_name is None:
            return process_module_template_errors

        template = get_global_cache(["module_template", template_name, "definition"])

        if template is None:
            process_module_template_errors.append(
                {
                    "file_path": get_global_cache(["module", module_code, "file_path"]),
                    "msg": f"Le template template_name='{template_name}' n'a pas été trouvé",
                }
            )
            return process_module_template_errors

        # EN COURS
        # Comment trouver un moyen efficace de faire du templating de dictionnaire en python ?????

        definition_with_template = copy.deepcopy(template)
        definition_with_template["module_code"] = definition["module_code"]
        definition_with_template["module"] = definition["module"]

        definition_with_template = replace_in_dict(
            definition_with_template, "M.MODULE_CODE", module_code
        )

        set_global_cache(["module", module_code, "definition"], definition_with_template)

        return process_module_template_errors
