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
    def get_layouts(cls):
        """
        renvoie la liste des layouts destinées au frontend
        """

        layouts = {}

        # faire ça dans init_layout ???
        for layout_name in cls.layout_names():
            # récupération depuis le cache
            layouts[layout_name] = copy.deepcopy(
                get_global_cache(["layout", layout_name, "definition"])
            )
            # on enlève layout_name ??
            # TODO à gérer en frontend
            layouts[layout_name].pop("layout_name")

        return layouts
