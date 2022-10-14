'''
    classe pour gérer la configuration des modules
'''

from sys import prefix
from . import errors
from ..schema import SchemaMethods
import os
from pathlib import Path
import copy
from flask import g, jsonify, Blueprint, current_app

from geonature.core.gn_permissions.tools import (
    cruved_scope_for_user_in_module,
)

cache_modules_config = {}


class ModulesConfig():

    @classmethod
    def module_config(cls, module_code):
        if module_code not in cls.modules_config():
            raise errors.ModuleNotFound(
                "La config du module de code {} n'a pas été trouvée"
                .format(module_code)
            )
        return cls.modules_config()[module_code]

    @classmethod
    def modules_config_db(cls):
        '''
            récupère les information des modules dans la base
        '''

        modules_config_db = {}
        module_schema = SchemaMethods('commons.module')
        if not module_schema.sql_table_exists():
            return {}

        modules_dict = module_schema.serialize_list(
            module_schema.query_list().all(),
            fields=[
                'module_code',
                'module_picto',
                'module_desc',
                'module_label',
                'module_path'
            ]
        )

        for module in modules_dict:
            modules_config_db[module['module_code']] = module

        return modules_config_db

    @classmethod
    def modules_config_files(cls):
        '''
            Récupère les information des modules depuis les fichiers 'module.yml'
        '''

        # parcours des fichiers
        module_files = {}
        for root, dirs, files in os.walk(SchemaMethods.config_directory(), followlinks=True):
            for file in filter(
                lambda f: 'config/modules' in root and f == 'module.yml',
                files
            ):
                file_path = Path(root) / file
                module_file = SchemaMethods.load_yml_file(file_path, load_keys=True)
                module_file['module_dir_path'] = str(file_path.parent)

                # gestion de la hierarchie entre les pages
                cls.process_tree(module_file)

                module_code = module_file['module']['module_code']
                module_files[module_code] = module_file

        return module_files

    @classmethod
    def process_tree(cls, module_config):
        '''
            gere les kety et parent pour chaque page de la config
        '''
        tree = module_config.get('tree')

        if not tree:
            return

        objects = {}
        cls.process_objects_from_tree(tree, objects)

        # find root
        page_root = None
        for page_name, page_config in module_config['pages'].items():
            if page_config['url'] == "":
                page_root = page_name
                page_config['root'] = True


        # gestion des pages
        # assignation de key et parent (et type ????) shema_name etc ???
        for page_name, page_config in module_config['pages'].items():

            page_key = '_'.join(page_name.split('_')[:-1])
            page_type = page_name.split('_')[-1]

            page_parent = None
            if objects.get(page_key, {}).get('parent'):
                page_parent = f"{objects.get(page_key, {}).get('parent')}_details"
            # assignations
            page_config['key'] = page_key
            page_config['type'] = page_type
            if page_parent:
                page_config['parent'] = page_parent
            elif page_root and page_root != page_name:
                page_config['parent'] = page_root

    @classmethod
    def process_objects_from_tree(cls, tree, objects, parent_key=None):
        '''
        '''

        if isinstance(tree, dict):
            for key, value in tree.items():
                if not key in objects:
                    objects[key] = {}
                    if parent_key:
                        objects[key]['parent'] = parent_key
                cls.process_objects_from_tree(value, objects, key)

    @classmethod
    def modules_config(cls):
        '''
        renvoie la configuration des modules
            - fichier module.yml
            - données de la base (gn_commons.t_modules, m_modules.t_module_groups, ...)
        '''

        if cache_modules_config != {}:
            return cache_modules_config

        modules_config = cls.init_modules()
        return modules_config

    @classmethod
    def init_modules(cls):
        # initialisation
        SchemaMethods.init_schemas_definitions()

        modules_config_db = cls.modules_config_db()
        modules_config_files = cls.modules_config_files()

        modules_config = {}

        for module_code in modules_config_db:
            if module_code not in modules_config_files:
                continue

        for module_code, module_config in modules_config_files.items():

            module_db = modules_config_db.get(module_code, {})
            module_config['registred'] = module_db != {}

            for key in (module_db or {}):
                module_config['module'][key] = module_config['module'].get(key, module_db[key])

            modules_config[module_code] = module_config

        for key, module_config in modules_config.items():
            cache_modules_config[key] = module_config

        for key in modules_config:
            cls.process_module_data(key)

        for key in modules_config:
            cls.process_module_params(key)

        for key in modules_config:
            cls.process_module_api(key)
        return modules_config

    @classmethod
    def process_module_params(cls, module_code):
        '''
            résolution de tous les champs contenus dans module_config['params']
        '''
        module_config = cls.module_config(module_code)
        params = module_config.get('params') or {}
        objects =  module_config['objects'] or {}
        processed_params = {}

        for key_param, param_config in params.items():
            schema_name = (
                module_config['objects'][param_config['object_name']].get('schema_name')
                or
                param_config['object_name']
            )

            sm = SchemaMethods(schema_name)

            m = (
                sm
                .get_row(param_config['value'], param_config['field_name'])
                .one()
            )

            processed_value = getattr(m, key_param)

            processed_params[key_param] = processed_value

        module_config['params'] = processed_params

        processed_objects = None

        for param_key, param_value in processed_params.items():
            processed_objects = cls.replace_in_dict(objects, f':{param_key}', param_value)

        if processed_objects:
            module_config['objects'] = processed_objects


    @classmethod
    def replace_in_dict(cls, data, field_name, value):

        if isinstance(data, dict):
            return {
                key: cls.replace_in_dict(val, field_name, value)
                for key, val in data.items()
            }

        if isinstance(data, list):
            return [ cls.replace_in_dict(item, field_name, value) for item in data]

        if isinstance(data, str):
            if data == field_name:
                return value
            if field_name in data:
                return data.replace(field_name, str(value))

        return data

    @classmethod
    def process_module_data(cls, module_code):
        module_config = cls.module_config(module_code)

        module_config['definitions'] = {}

        for object_name, object_definition in module_config['objects'].items():
            object_definition = object_definition
            object_definition['schema_name'] = object_definition.get('schema_name', object_name)
            sm = SchemaMethods(object_definition['schema_name'])
            module_config['definitions'][object_name] = sm.config()


    @classmethod
    def process_module_api(cls, module_code):
        module_config = cls.module_config(module_code)

        bp = Blueprint(module_code, __name__)
        for object_name, object_definition in module_config['objects'].items():
            sm = SchemaMethods(object_definition['schema_name'])

            # ouverture des routes
            sm.register_api(bp, module_code, object_name, copy.deepcopy(object_definition))

            if 'prefilters' in  object_definition:
                del object_definition['prefilters']

        current_app.register_blueprint(bp, url_prefix=f'/{module_code.lower()}')


    @classmethod
    def modules_config_with_rigths(cls):
        modules_config = copy.deepcopy(cls.modules_config())

        # pour ne pas exposer module_dir_path
        for key, module_config in modules_config.items():
            module_config.pop('module_dir_path')

        if not hasattr(g, 'current_user'):
            return modules_config

        # on calcule le cruved ici pour ne pas interférer avec le cache
        # pour chaque module
        for key, module_config in modules_config.items():
            # pour chaque type de droit dans 'CRUVED'
            module_config['cruved'] = {
                k: int(v)
                for k, v in cruved_scope_for_user_in_module(
                    g.current_user.id_role,
                    module_code=module_config['module']['module_code']
                )[0].items()
            }

        return modules_config

    @classmethod
    def process_dict_path(cls, d, dict_path, base_url):
        '''
            return dict or dict part according to path
            process error if needed
        '''

        if not dict_path:
            return d

        p_error = []
        out = copy.deepcopy(d)
        for p in dict_path.split('/'):
            if p:
                # gestion des indices des listes
                try:
                    p = int(p)
                except Exception:
                    pass
                try:
                    out = out[p]
                    p_error.append(p)
                except Exception:
                    path_error = '/'.join(p_error)
                    txt_error = "La chemin demandé <b>{}/{}</b> n'est pas correct\n".format(path_error, p)
                    if type(out) is dict and out.keys():
                        txt_error += "<br><br>Vous pouvez choisir un chemin parmi :"
                        for key in sorted(list(out.keys())):
                            url_key = base_url  + path_error + "/" + key
                            txt_error += '<br> - <a href="{}">{}{}</a>'.format(url_key, path_error + '/' if path_error else '', key)
                    return txt_error, 500

        return jsonify(out)

    @classmethod
    def process_commons_api(cls, blueprint):
        '''
            ouverture des routes de listes avec module_code = MODULES
        '''

        for schema_name in [
            'ref_geo.area'
        ]:
            SchemaMethods(schema_name).register_api(blueprint, 'MODULES', schema_name)