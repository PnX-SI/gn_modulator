import copy
from gn_modules.utils.cache import get_global_cache


class BaseLayout:
    @classmethod
    def layout_codes(cls):
        """
        renvoie la listes des layount_names trouvés dans les définitions
        """

        return list(get_global_cache(["layout"]).keys())

    @classmethod
    def layout_template_codes(cls):
        """
        renvoie la listes des templates de layout
        """

        return list(
            filter(
                lambda x: get_global_cache(["template", x, "definition"])["template"]["type"]
                == "layout",
                get_global_cache(["template"]).keys(),
            )
        )

    @classmethod
    def get_layout(cls, layout_code, is_template=False):
        """
        renvoie un layout pour un layout_code donné
        """

        definition_type = "template" if is_template else "layout"
        layout = get_global_cache([definition_type, layout_code, "definition"])
        return layout

    @classmethod
    def get_layouts(
        cls, layout_search_code=None, layout_code=None, as_dict=False, is_template=False
    ):
        """
        renvoie la liste des layouts destinées au frontend
        """

        layout_codes = cls.layout_template_codes() if is_template else cls.layout_codes()

        if layout_code:
            return cls.get_layout(layout_code, is_template)

        if layout_search_code:
            layout_codes = filter(
                lambda x: layout_search_code is None or layout_search_code in x, layout_codes
            )

        if as_dict:
            layouts_as_dict = {}
            for layout_code in layout_codes:
                layout = copy.deepcopy(cls.get_layout(layout_code, is_template))
                # layout.pop("layout_code")
                layouts_as_dict[layout_code] = layout
            return layouts_as_dict

        return [
            cls.get_layout(layout_code, is_template)
            # faire ça dans init_layout ???
            for layout_code in layout_codes
        ]
