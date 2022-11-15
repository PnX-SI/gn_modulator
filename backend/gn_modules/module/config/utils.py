from gn_modules.schema import SchemaMethods
from flask import Blueprint, current_app
import copy
from gn_modules.utils.commons import replace_in_dict
from gn_modules.utils.cache import get_global_cache, set_global_cache


class ModuleConfigUtils:
    @classmethod
    def object_config(cls, module_code, object_name):
        """
        Retourne la configuration d'un object
        - référencé par 'object_name'
        - et pour le module 'module_code'
        """
        module_config = cls.module_config(module_code)
        object_config = module_config.get("objects", {}).get(object_name)

        if not object_config:
            raise cls.errors.ModuleObjectNotFoundError(
                f"L'object {object_name} n'a pas été trouvé pour le module {module_code}"
            )

        return object_config

    @classmethod
    def process_tree(cls, module_code):
        """
        gere les ket et parent pour chaque page de la config
        """

        module_config = cls.module_config(module_code)
        tree = module_config.get("tree")

        if not tree:
            return

        objects = {}
        cls.process_objects_from_tree(tree, objects)

        # find root
        page_root = None
        for page_name, page_config in module_config["pages"].items():
            if page_config["url"] == "":
                page_root = page_name
                page_config["root"] = True

        # gestion des pages
        # assignation de key et parent (et type ????) shema_name etc ???
        for page_name, page_config in module_config["pages"].items():
            page_key = "_".join(page_name.split("_")[:-1])
            page_type = page_name.split("_")[-1]

            page_parent = None
            if objects.get(page_key, {}).get("parent"):
                page_parent = f"{objects.get(page_key, {}).get('parent')}_details"
            # assignations
            page_config["key"] = page_key
            page_config["type"] = page_type
            if page_parent:
                page_config["parent"] = page_parent
            elif page_root and page_root != page_name:
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

        for key_param, param_config in params.items():
            schema_name = (
                param_config.get("schema_name")
                or module_config["objects"][param_config["object_name"]].get(
                    "schema_name"
                )
                or param_config["object_name"]
            )

            m = (
                SchemaMethods(schema_name)
                .get_row(param_config["value"], param_config["field_name"], params={})
                .one()
            )

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

        for object_name, object_module_config in module_config["objects"].items():

            object_module_config["schema_name"] = object_module_config.get(
                "schema_name", object_name
            )

            if object_module_config["schema_name"] not in module_config["schemas"]:
                module_config["schemas"].append(object_module_config["schema_name"])

            object_module_config["object_name"] = object_name

            # on récupère la configuration du schéma avec la possibilité de changer certains paramètre
            # comme par exemple 'label', 'labels', 'genre'
            object_schema_config = SchemaMethods(
                object_module_config["schema_name"]
            ).config(object_module_config)

            # insertion de la config schema dans la config module
            for key, _object_schema_config_item in object_schema_config.items():
                # copie pour ne pas rendre les modifications persistantes
                object_schema_config_item = copy.deepcopy(_object_schema_config_item)

                # si la clé est déjà présente dans object_module_config
                # en prend en compte les clé de object_module_config et object_schema_config
                # avec une priorité sur la configuration d'lobject au niveau du module (object_module_config)
                if (key in object_module_config) and isinstance(
                    _object_schema_config_item, dict
                ):
                    object_schema_config_item.update(object_module_config[key])
                    object_module_config[key] = object_schema_config_item

                # sinon assignation simple
                else:
                    object_module_config[key] = object_schema_config_item

        # Traitement des exports
        # a faire dans definition
        # - pour chaque export défini dans la config du module
        for export_name, export_definition in module_config.get("exports", {}).items():

            #  - on lui assigne son export_name
            export_definition["export_name"] = export_name

            # test si l'export existe déjà
            if get_global_cache(["exports", export_name]):
                raise cls.errors.ModuleConfigError(
                    f"L'export {export_name} à déjà été défini par ailleurs, le code de l'export doit être unique"
                )

            #  - on l'assigne à son object
            object_config = module_config["objects"][export_definition["object_name"]]
            object_config["exports"] = object_config.get("exports", [])
            object_config["exports"].append(export_name)

            # mise en cache pour pouvoir s'en reservir par ailleurs
            set_global_cache(["exports", export_name], export_definition)

    @classmethod
    def process_module_api(cls, module_code):

        module_config = cls.module_config(module_code)

        bp = Blueprint(module_code, __name__)
        for object_name, object_definition in module_config["objects"].items():
            sm = SchemaMethods(object_definition["schema_name"])

            # ouverture des routes
            sm.register_api(
                bp, module_code, object_name, copy.deepcopy(object_definition)
            )

            if "prefilters" in object_definition:
                del object_definition["prefilters"]

        current_app.register_blueprint(bp, url_prefix=f"/{module_code.lower()}")
