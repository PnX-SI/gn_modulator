import copy
from gn_modules.utils.cache import get_global_cache


class BaseLayout:
    @classmethod
    def layout_names(cls):
        """
        renvoie la listes des layount_names trouvés dans les définitions
        """

        return list(get_global_cache(["layout"]).keys())

    @classmethod
    def get_layout(cls, layout_name):
        """
        renvoie un layout pour un layout_name donné
        """

        layout = get_global_cache(["layout", layout_name, "definition"])
        return layout

    @classmethod
    def get_layouts(cls, layout_search_name=None, layout_name=None, as_dict=False):
        """
        renvoie la liste des layouts destinées au frontend
        """

        layout_names = cls.layout_names()

        if layout_name:
            return get_global_cache(["layout", layout_name, "definition"])

        if layout_search_name:
            layout_names = filter(
                lambda x: layout_search_name is None or layout_search_name in x, layout_names
            )

        if as_dict:
            layouts_as_dict = {}
            for layout_name in layout_names:
                layout = copy.deepcopy(cls.get_layout(layout_name))
                layout.pop("layout_name")
                layouts_as_dict[layout_name] = layout
            return as_dict

        return [
            cls.get_layout(layout_name)
            # faire ça dans init_layout ???
            for layout_name in layout_names
        ]
