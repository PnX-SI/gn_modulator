from gn_modules.schema import SchemaMethods
from flask import Blueprint, current_app
import copy
from gn_modules.utils.commons import replace_in_dict
from gn_modules.utils.cache import get_global_cache, set_global_cache


class ModuleConfigUtils:
    @classmethod
    def object_config(cls, module_code, object_code):
        """
        Retourne la configuration d'un object
        - référencé par 'object_code'
        - et pour le module 'module_code'
        """
        module_config = cls.module_config(module_code)
        object_config = module_config.get("objects", {}).get(object_code)

        if not object_config:
            raise cls.errors.ModuleObjectNotFoundError(
                f"L'object {object_code} n'a pas été trouvé pour le module {module_code}"
            )

        return object_config

    @classmethod
    def schema_code(cls, module_code, object_code):
        object_config = cls.object_config(module_code, object_code)
        return object_config["schema_code"]

    @classmethod
    def layout_code(cls, module_code, object_code, action):
        return f"{module_code}.{object_code}_{action}"

    @classmethod
    def page_code(cls, object_code, action):
        return f"{object_code}_{action}"

    @classmethod
    def page_url(cls, module_code, object_code, action):
        if action in ["details", "edit"]:
            sm = SchemaMethods(cls.schema_code(module_code, object_code))
            return f"{object_code}_{action}/:{sm.pk_field_name()}"
        else:
            return f"{object_code}_{action}"

    @classmethod
    def default_page_config(cls, module_code, object_code, action):

        sm = SchemaMethods(cls.schema_code(module_code, object_code))
        default_page_config = {
            "action": action,
            "code": cls.page_code(object_code, action),
            "url": cls.page_url(module_code, object_code, action),
            # "layout": {"code": cls.layout_code(module_code, object_code, action)},
            "object_code": object_code,
        }

        if action in ["details", "edit"]:
            default_page_config["objects"] = {object_code: {"value": f":{sm.pk_field_name()}"}}

        return default_page_config

    @classmethod
    def process_pages(cls, module_code):
        module_config = cls.module_config(module_code)

        pages_definition = module_config.get("pages_definition")

        pages = module_config.get("pages")

        if pages or not pages_definition:
            return

        pages = {}

        for object_code, object_pages_config in pages_definition.items():
            for action, page_action_config in object_pages_config.items():
                page_config = copy.deepcopy(
                    cls.default_page_config(module_code, object_code, action)
                )
                for elem_key, elem_value in page_action_config.items():
                    if elem_key == "objects":
                        for object_code_, object_config_ in elem_value.items():
                            page_config["objects"][object_code_] = object_config_
                    else:
                        page_config[elem_key] = elem_value

                pages[page_config["code"]] = page_config

        module_config["pages"] = pages

    @classmethod
    def process_tree(cls, module_code):
        """
        gere les ket et parent pour chaque page de la config
        """

        module_config = cls.module_config(module_code)
        tree = module_config.get("tree")

        if not tree:
            return

        objects_with_parent = {}
        cls.process_objects_from_tree(tree, objects_with_parent)

        # find root
        page_root = None
        for page_code, page_config in module_config.get("pages", {}).items():
            if page_config.get("root"):
                page_root = page_code
                page_config["url"] = ""

        # gestion des pages
        # assignation de key et parent (et type ????) shema_name etc ???
        for page_code, page_config in module_config.get("pages", {}).items():
            object_code = page_config["object_code"]
            page_parent = None
            object_parent = objects_with_parent.get(object_code, {}).get("parent")
            if object_parent:
                page_parent = f"{object_parent}_details"
            # assignations

            if page_parent:
                page_config["parent"] = page_parent
            elif page_root and page_root != page_code:
                page_config["parent"] = page_root

    @classmethod
    def process_objects_from_tree(cls, tree, objects, parent_key=None):
        """ """

        if isinstance(tree, dict):
            for key, value in tree.items():
                if key not in objects:
                    objects[key] = {}
                    if parent_key:
                        objects[key]["parent"] = parent_key
                cls.process_objects_from_tree(value, objects, key)

    @classmethod
    def process_module_params(cls, module_code):
        """
        résolution de tous les champs contenus dans module_config['params']
        """

        module_config = cls.module_config(module_code)

        params = module_config.get("params") or {}
        objects = module_config["objects"] or {}
        processed_params = {}

        # on boucle sur tous les éléments de params
        for key_param, param_config in params.items():

            # récupération du schema (par ordre de priorité)
            # - depuis schema_code
            # - depuis object_code -> schema_code de l'object
            schema_code = (
                param_config.get("schema_code")
                or module_config["objects"][param_config["object_code"]].get("schema_code")
                or param_config["object_code"]
            )

            field_names = list(param_config["value"].keys())
            values = list(param_config["value"].values())

            m = SchemaMethods(schema_code).get_row(values, field_names).one()

            processed_value = getattr(m, key_param)
            processed_params[key_param] = processed_value

        module_config["params"] = processed_params

        processed_objects = None

        for param_key, param_value in processed_params.items():
            processed_objects = replace_in_dict(objects, f":{param_key}", param_value)

        if processed_objects:
            module_config["objects"] = processed_objects

    @classmethod
    def process_module_objects(cls, module_code):
        """
        - object_module_config : configuration provenant du module.yml
        - object_schema_config : configuration provenant de la definition
        """

        module_config = cls.module_config(module_code)

        module_config["schemas"] = []

        for object_code, object_module_config in module_config["objects"].items():

            object_module_config["schema_code"] = object_module_config.get(
                "schema_code", object_code
            )

            if object_module_config["schema_code"] not in module_config["schemas"]:
                module_config["schemas"].append(object_module_config["schema_code"])

            object_module_config["object_code"] = object_code

            # on récupère la configuration du schéma avec la possibilité de changer certains paramètre
            # comme par exemple 'label', 'labels', 'genre'
            object_schema_config = SchemaMethods(object_module_config["schema_code"]).config(
                object_module_config
            )

            # insertion de la config schema dans la config module
            for key, _object_schema_config_item in object_schema_config.items():
                # copie pour ne pas rendre les modifications persistantes
                object_schema_config_item = copy.deepcopy(_object_schema_config_item)

                # si la clé est déjà présente dans object_module_config
                # en prend en compte les clé de object_module_config et object_schema_config
                # avec une priorité sur la configuration d'lobject au niveau du module (object_module_config)
                if (key in object_module_config) and isinstance(_object_schema_config_item, dict):
                    object_schema_config_item.update(object_module_config[key])
                    object_module_config[key] = object_schema_config_item

                # sinon assignation simple
                else:
                    object_module_config[key] = object_schema_config_item

        # Traitement des exports
        # a faire dans definition
        # - pour chaque export défini dans la config du module
        for export_code, export_definition in module_config.get("exports", {}).items():

            #  - on lui assigne son export_code
            export_definition["export_code"] = export_code

            # test si l'export existe déjà
            if get_global_cache(["exports", export_code]):
                raise cls.errors.ModuleConfigError(
                    f"L'export {export_code} à déjà été défini par ailleurs, le code de l'export doit être unique"
                )

            #  - on l'assigne à son object
            object_config = module_config["objects"][export_definition["object_code"]]
            object_config["exports"] = object_config.get("exports", [])
            object_config["exports"].append(export_code)

            # mise en cache pour pouvoir s'en reservir par ailleurs
            set_global_cache(["exports", export_code], export_definition)

    @classmethod
    def process_module_api(cls, module_code):
        """
        ouvre les routes pour un module
        """

        module_config = cls.module_config(module_code)

        bp = Blueprint(module_code, __name__)

        # pour tous les object d'un module
        for object_code, object_definition in module_config["objects"].items():

            # on récupère schema methodes
            sm = SchemaMethods(object_definition["schema_code"])

            # ouverture des routes pour ce schema
            #   - avec les options:'object_definition'
            #     en particulier le cruved
            sm.register_api(bp, module_code, object_code, copy.deepcopy(object_definition))

            # les prefiltres définis dans les objects ne servent que dans les ouverture de route ???
            if "prefilters" in object_definition:
                del object_definition["prefilters"]

        # enregistrement du blueprint pour ce module
        current_app.register_blueprint(bp, url_prefix=f"/{module_code.lower()}")
