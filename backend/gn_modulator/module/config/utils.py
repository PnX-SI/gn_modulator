from gn_modulator.schema import SchemaMethods
from flask import Blueprint, current_app
import copy
from gn_modulator.utils.commons import replace_in_dict
from gn_modulator.utils.cache import get_global_cache, set_global_cache


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
    def page_url(cls, module_code, object_code, action, pk_field_name):
        if action in ["details", "edit"]:
            return f"{object_code}_{action}/:{pk_field_name}"
        else:
            return f"{object_code}_{action}"

    @classmethod
    def default_page_config(cls, module_code, object_code, action):
        try:
            sm = SchemaMethods(cls.schema_code(module_code, object_code))
            pk_field_name = sm.pk_field_name()
        except Exception:
            pk_field_name = "id_xxx"

        default_page_config = {
            "action": action,
            "code": cls.page_code(object_code, action),
            "url": cls.page_url(module_code, object_code, action, pk_field_name),
            "layout": {"code": cls.layout_code(module_code, object_code, action)},
            "object_code": object_code,
        }

        if action in ["details", "edit"]:
            default_page_config["objects"] = {object_code: {"value": f":{pk_field_name}"}}

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
                for elem_key, elem_value in (page_action_config or {}).items():
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
            try:
                object_schema_config = SchemaMethods(object_module_config["schema_code"]).config(
                    object_module_config
                )
            except Exception:
                object_schema_config = {}

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
        # for export_code, export_definition in module_config.get("exports", {}).items():
        #     #  - on lui assigne son export_code
        #     export_definition["export_code"] = export_code

        #     # test si l'export existe déjà
        #     if get_global_cache(["exports", export_code]):
        #         raise cls.errors.ModuleConfigError(
        #             f"L'export {export_code} à déjà été défini par ailleurs, le code de l'export doit être unique"
        #         )

        #     #  - on l'assigne à son object
        #     object_config = module_config["objects"][export_definition["object_code"]]
        #     object_config["exports"] = object_config.get("exports", [])
        #     object_config["exports"].append(export_code)

        #     # mise en cache pour pouvoir s'en reservir par ailleurs
        #     set_global_cache(["exports", export_code], export_definition)

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

    @classmethod
    def process_fields(cls, module_code):
        """
        On regarde dans toutes les pages pour déterminer les champs
        """
        cls.process_base_fields(module_code)
        cls.process_layout_fields(module_code)

    @classmethod
    def process_base_fields(cls, module_code):
        module_config = cls.module_config(module_code)
        if not module_config["registred"]:
            return
        for object_code in module_config["objects"]:
            object_config = cls.object_config(module_code, object_code)
            if "R" in object_config["cruved"]:
                cls.add_basic_fields(module_code, object_code)

    @classmethod
    def add_basic_fields(cls, module_code, object_code):
        sm = SchemaMethods(cls.schema_code(module_code, object_code))
        if sm.definition is None:
            return
        authorized_read_fields = (
            get_global_cache(
                [
                    "keys",
                    module_code,
                    object_code,
                    "read",
                ]
            )
            or []
        )

        authorized_write_fields = (
            get_global_cache(
                [
                    "keys",
                    module_code,
                    object_code,
                    "read",
                ]
            )
            or []
        )

        set_global_cache(
            [
                "keys",
                module_code,
                object_code,
                "read",
            ],
            authorized_read_fields,
        )

        set_global_cache(
            [
                "keys",
                module_code,
                object_code,
                "write",
            ],
            authorized_write_fields,
        )

        # pour la lecture, on ajoute par défaut les champs
        # - pk_field_name
        # - label_field_name
        # - title_field_name
        # - champs d'unicité
        # - scope
        for elem in [
            sm.pk_field_name(),
            sm.label_field_name(),
            sm.title_field_name(),
            sm.geometry_field_name(),
            *sm.unique(),
            "scope",
        ]:
            if elem is not None and elem not in authorized_read_fields:
                authorized_read_fields.append(elem)

    @classmethod
    def process_layout_fields(cls, module_code):
        module_config = cls.module_config(module_code)

        pages = module_config.get("pages", {})
        config_params = module_config.get("config_params", {})
        config_defaults = module_config.get("config_defaults", {})
        config_params = {**config_defaults, **config_params}
        context = {"module_code": module_code}
        for page_code in pages:
            cls.get_layout_keys(pages[page_code]["layout"], config_params, context)

    @classmethod
    def get_layout_keys(cls, layout, params, context):
        #
        if isinstance(layout, list):
            for item in layout:
                cls.get_layout_keys(item, params, context)
            return

        # ajout d'une clé
        if isinstance(layout, str):
            return cls.add_key(context, layout)

        if layout.get("key") and layout.get("type") not in ["dict", "array"]:
            cls.add_key(context, layout["key"])

        if layout.get("object_code"):
            context = {**context, "object_code": layout["object_code"]}

        if layout.get("type") == "form":
            context = {**context, "form": True}

        if layout.get("module_code"):
            context = {**context, "module_code": layout["module_code"]}

        # traitement dict array
        if isinstance(layout, dict) and layout.get("type") in ["dict", "array"]:
            data_keys = context.get("data_keys", [])
            data_keys.append(layout["key"])
            context = {**context, "data_keys": data_keys}
            return cls.get_layout_keys(layout["items"], params, context)

        # traitement list_form
        if layout.get("type") == "list_form":
            key_add = []
            if layout.get("label_field_name"):
                key_add.append(layout["label_field_name"])
            if layout.get("title_field_name"):
                key_add.append(layout["title_field_name"])
            if layout.get("additional_fields"):
                key_add += layout["additional_fields"]
            if key_add:
                cls.get_layout_keys(
                    key_add,
                    params,
                    {**context, "data_keys": []},
                )
            if (
                layout.get("return_object")
                and layout.get("additional_fields")
                and not context.get("form")
            ):
                additional_keys = list(
                    map(lambda x: f"{layout['key']}.{x}", layout["additional_fields"])
                )
                cls.get_layout_keys(additional_keys, params, context)

        if layout.get("code"):
            template_params = {**params, **layout.get("template_params", {})}
            layout_from_code = SchemaMethods.get_layout_from_code(
                layout.get("code"), template_params
            )
            return cls.get_layout_keys(layout_from_code, params, context)

        if layout.get("items"):
            return cls.get_layout_keys(layout.get("items"), params, context)

    @classmethod
    def add_key(cls, context, key):
        keys = get_global_cache(["keys"])
        if context.get("data_keys"):
            key = f"{''.join(context['data_keys'])}.{key}"

        module_keys = keys[context["module_code"]] = keys.get(context["module_code"], {})
        object_keys = module_keys[context["object_code"]] = module_keys.get(
            context["object_code"], {"read": [], "write": []}
        )

        object_config = cls.object_config(context["module_code"], context["object_code"])
        schema_code = object_config["schema_code"]

        sm = SchemaMethods(schema_code)
        if sm.definition is None:
            return

        if not sm.has_property(key):
            # raise error ?
            print(f"pb ? {sm} has no {key}")
            return keys

        # ajout en lecture
        if key not in object_keys["read"]:
            object_keys["read"].append(key)

        # ajout en ecriture
        if context.get("form"):
            # key si relationship
            write_key = key
            if sm.is_relationship(key):
                rel = SchemaMethods(sm.property(key)["schema_code"])
                write_key = f"{key}.{rel.pk_field_name()}"
            if write_key not in object_keys["write"]:
                object_keys["write"].append(write_key)
        return keys

    @classmethod
    def get_autorized_fields(cls, module_code, object_code, write=False):
        return get_global_cache(
            [
                "keys",
                module_code,
                object_code,
                "write" if write else "read",
            ]
        )
