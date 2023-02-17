"""
    methodes pour les layout ajsf du frontend
"""

from gn_modulator.definition import DefinitionMethods
import copy
from gn_modulator.utils.commons import replace_in_dict
from gn_modulator.utils.errors import add_error


class SchemaConfigLayout:
    def form_layout(self):
        """
        layout destiné au composant formulaire du frontend
        """

        # - soit $meta.form.layout est defini,
        # - ou alors toutes les cle de properties

        form_layout = self.attr("form.layout", list(self.properties().keys()))

        return self.process_layout(form_layout)

    def process_layout(self, layout):
        """
        récupérer les infos d'une clé depuis les définitions
        """

        if isinstance(layout, dict):
            if "key" in layout:
                if "." in layout["key"] and len(layout["key"].split(".")) == 2:
                    definition = self.property(layout["key"].split(".")[0])
                    layout["title"] = layout.get("title", definition["title"])

                if not self.has_property(layout["key"]):
                    return layout
                definition = self.property(layout["key"])
                layout["required"] = (
                    layout["required"]
                    if layout.get("required") is not None
                    else self.is_required(layout["key"])
                )
                for key in [
                    "title",
                    "description",
                    "type",
                    "schema_code",
                    "nomenclature_type",
                    "min",
                    "max",
                    "change",
                    "placeholder",
                    "disabled",
                ]:
                    if key in definition:
                        layout[key] = layout.get(key, definition[key])

                if layout["type"] in ["array", "object"] and layout.get("schema_code"):
                    rel = self.cls(layout["schema_code"])
                    layout["items"] = rel.process_layout(layout["items"])
                return layout

            return {k: self.process_layout(v) for k, v in layout.items()}

        if isinstance(layout, list):
            return [self.process_layout(elem) for elem in layout]

        if (
            isinstance(layout, str)
            and (not layout.startswith("__f__"))
            and self.has_property(layout)
        ):
            return self.process_layout({"key": layout})

        return layout

    @classmethod
    def get_layout_from_code(cls, layout_code, params):
        layout_from_code = copy.deepcopy(DefinitionMethods.get_definition("layout", layout_code))
        if layout_from_code is None:
            add_error(
                msg=f"Le layout de code {layout_code} n'existe pas",
                definition_type="layout",
                definition_code=layout_code,
                code="ERR_TEMPLATE_NOT_FOUND",
            )
        layout_from_code = layout_from_code["layout"]
        for param_key, param_item in params.items():
            layout_from_code = replace_in_dict(
                layout_from_code, f"__{param_key.upper()}__", param_item
            )

        unresolved_template_params = DefinitionMethods.get_unresolved_template_params(
            layout_from_code
        )
        if unresolved_template_params:
            remindings__str = ", ".join(map(lambda x: f"__{x}__", unresolved_template_params))
            add_error(
                msg=f"Le ou les champs suivants n'ont pas été résolus : {remindings__str}",
                definition_type="layout",
                definition_code=layout_code,
                code="ERR_TEMPLATE_UNRESOLVED_FIELDS",
                template_file_path=str(DefinitionMethods.get_file_path("layout", layout_code)),
            )

            return {}

        return layout_from_code
