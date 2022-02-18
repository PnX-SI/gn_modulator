import os
from pathlib import Path
from ..schema import SchemaMethods
from sqlalchemy.orm.exc import NoResultFound
from flask import g
from geonature.core.gn_permissions.tools import (
    cruved_scope_for_user_in_module,
)

from . import errors

cache_modules_config = {}

class ModuleBase():

    @classmethod
    def install_module(cls, module_code):

        # insert module in gn_commons.t_modules and gn_modules.t_module_complements
        cls.register_or_update_module(module_code)

        # process module data (nomenclature, groups ?, datasets, etc..)
        cls.process_module_sql(module_code)

        # process module data (nomenclature, groups ?, datasets, etc..)
        cls.process_module_data(module_code)

        return

    @classmethod
    def module_config(cls, module_code):
        if module_code not in cls.modules_config():
            raise errors.ModuleNotFound(
                "La config du module de code {} n'a pas été trouvée"
                .format(module_code)
            )
        return cls.modules_config()[module_code]

    @classmethod
    def register_or_update_module(cls, module_code):

        schema_module = SchemaMethods('modules.module')
        module_data = cls.module_config(module_code)['module']
        module_code = module_data['module_code']
        module_row_data = {
            'module_label': module_data['module_label'],
            'module_desc': module_data['module_desc'],
            'module_picto': module_data['module_picto'],
            'active_frontend': module_data['active_frontend'],
            'module_code': module_code,
            'module_name': module_code,
            'module_path': 'modules/{}'.format(module_code.lower()),
            'active_backend': False,
        }

        try:
            _, b_update = schema_module.update_row(module_code, module_row_data, field_name='module_code')

            print("Le module {} existe déjà".format(module_code))
            if b_update:
                print('Mise à jour')
            return

        except NoResultFound:
            pass

            schema_module.insert_row(module_row_data)

            print('Le module {} à bien été enregistré'.format(module_code))
            return

    @classmethod
    def save_sql_txt(cls, module_code, txt):

        module_config = cls.module_config(module_code)
        sql_dir = Path(module_config['module_dir_path']) / 'data'
        sql_dir.mkdir(parents=True, exist_ok=True)
        sql_file_path = sql_dir / 'schema_{}.sql'.format(module_code.lower())
        print('Sauvegarde du code sql dans {}'.format(sql_file_path))

        with open(sql_file_path, 'w') as f:
            f.write(txt)

    @classmethod
    def process_module_sql(cls, module_code):

        module_config = cls.module_config(module_code)
        schema_names = module_config['schemas']
        txt = ""
        for schema_name in schema_names:
            sm = SchemaMethods(schema_name)
            if sm.sql_schema_exists():
                return
            txt += sm.sql_txt_process()

        cls.save_sql_txt(module_code, txt)

        print('Exécution du code sql')
        SchemaMethods.c_sql_exec_txt(txt)
        pass

    @classmethod
    def process_module_features(cls, module_code):
        data_names = cls.module_config(module_code).get('features', [])
        infos = {}
        for data_name in data_names:
            infos[data_name] = SchemaMethods.process_data(data_name)
        pass
        SchemaMethods.log(SchemaMethods.txt_data_infos(infos))

    @classmethod
    def modules_db(cls):

        modules_db = {}
        module_schema = SchemaMethods('modules.module')
        query, _ = module_schema.get_list({})
        modules_dict = module_schema.serialize_list(query.all())

        for module in modules_dict:
            if hasattr(g, 'current_user'):
                module['cruved'] = cruved_scope_for_user_in_module(g.current_user.id_role, module_code=module['module_code'])[0]
            modules_db[module['module_code']] = module

        return modules_db

    @classmethod
    def modules_files(cls):
        module_files = {}
        for root, dirs, files in os.walk(SchemaMethods.config_directory(), followlinks=True):
            for file in filter(
                lambda f: 'config/modules' in root and f == 'module.json',
                files
            ):
                file_path = Path(root) / file
                module_file = SchemaMethods.load_json_file(file_path)
                module_file['module_dir_path'] = str(file_path.parent)
                module_code = module_file['module']['module_code']
                module_files[module_code] = module_file

        return module_files

    @classmethod
    def modules_config(cls):

        if cache_modules_config != {}:
            return cache_modules_config

        modules_db = cls.modules_db()
        modules_files = cls.modules_files()

        modules_config = {}

        for module_code in modules_db:
            if module_code not in modules_files:
                raise errors.ModuleDbError(
                    'Le module {} est en base et non trouvé dans les fichiers'
                    .format(module_code)
                )

        for module_code, module_config in modules_files.items():
            module_db = modules_db.get(module_code, {})
            module_config['registred'] = module_db != {}

            for key in (module_db or {}):
                module_config['module'][key] = module_db[key]
            modules_config[module_code] = module_config

        for key in modules_config:
            cache_modules_config[key] = modules_config[key]

        return modules_config

    @classmethod
    def process_module_data(cls, module_code):
        module_config = cls.module_config(module_code)
        data_names = module_config.get('features', [])
        for data_name in data_names:
            infos = {}
            file_path = Path(module_config['module_dir_path']) / 'features/{}'.format(data_name)
            infos[data_name] = SchemaMethods.process_data(file_path)
            SchemaMethods.log(SchemaMethods.txt_data_infos(infos))
        pass