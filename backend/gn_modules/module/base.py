import os
from pathlib import Path
from ..schema import SchemaMethods
from sqlalchemy.orm.exc import NoResultFound
from flask import g
from . import errors
from geonature.utils.env import BACKEND_DIR

cache_modules_config = {}

def symlink(path_source, path_dest):
    if(os.path.islink(path_dest)):
        os.remove(path_dest)
    os.symlink(path_source, path_dest)

class ModuleBase():

    @classmethod
    def migrations_dir(cls, module_code=None):
        if not module_code:
            return SchemaMethods.migrations_directory()
        module_config = cls.module_config(module_code)
        return Path(module_config['module_dir_path']) / 'migrations'

    @classmethod
    def module_config(cls, module_code):
        if module_code not in cls.modules_config():
            raise errors.ModuleNotFound(
                "La config du module de code {} n'a pas été trouvée"
                .format(module_code)
            )
        return cls.modules_config()[module_code]

    @classmethod
    def register_db_module(cls, module_code):
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
            schema_module.update_row(module_code, module_row_data, field_name='module_code')
        except NoResultFound:
            schema_module.insert_row(module_row_data, commit=True)
        print(module_data['module_desc'])
        print(schema_module.get_row(module_code, 'module_code').module_desc)

    @classmethod
    def delete_db_module(cls, module_code):
        schema_module = SchemaMethods('commons.module')
        schema_module.delete_row(module_code, field_name='module_code')

    # @classmethod
    # def register_or_update_module(cls, module_code):

    #     schema_module = SchemaMethods('modules.module')
    #     module_data = cls.module_config(module_code)['module']
    #     module_code = module_data['module_code']
    #     module_row_data = {
    #         'module_label': module_data['module_label'],
    #         'module_desc': module_data['module_desc'],
    #         'module_picto': module_data['module_picto'],
    #         'active_frontend': module_data['active_frontend'],
    #         'module_code': module_code,
    #         'module_name': module_code,
    #         'module_path': 'modules/{}'.format(module_code.lower()),
    #         'active_backend': False,
    #     }

    #     try:
    #         _, b_update = schema_module.update_row(module_code, module_row_data, field_name='module_code')

    #         print("Le module {} existe déjà".format(module_code))
    #         if b_update:
    #             print('Mise à jour')
    #         return

    #     except NoResultFound:
    #         pass

    #         schema_module.insert_row(module_row_data)

    #         print('Le module {} à bien été enregistré'.format(module_code))
    #         return


    @classmethod
    def create_schema_sql(cls, module_code, force=False):

        module_config = cls.module_config(module_code)
        schema_names = module_config['schemas']
        txt = ""
        for schema_name in schema_names:
            sm = SchemaMethods(schema_name)
            txt += sm.sql_txt_process()

        sql_file_path = cls.migrations_dir(module_code) / 'data/schema.sql'
        if sql_file_path.exists() and not force:
            print('- Le fichier existe déjà {}'.format(sql_file_path))
            print('- Veuillez relancer la commande avec -f pour forcer la réécriture')
            return
        sql_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sql_file_path, 'w') as f:
            f.write(txt)
        print('- Création du fichier {}'.format(sql_file_path.name))

    @classmethod
    def create_reset_sql(cls, module_code):
        sql_file_path = cls.migrations_dir(module_code) / 'data/reset.sql'
        if sql_file_path.exists:
            return
        sql_file_path.parent.mkdir(parents=True, exist_ok=True)

        module_config = cls.module_config(module_code)
        schema_names = module_config['schemas']
        txt = "--\n-- reset.sql ({})\n--\n\n".format(module_code)
        for schema_name in schema_names:
            sm = SchemaMethods(schema_name)
            txt_drop_schema = "-- DROP SCHEMA {} CASCADE;\n".format(sm.sql_schema_name())
            if txt_drop_schema not in txt:
                txt += txt_drop_schema

        with open(sql_file_path, 'w') as f:
            f.write(txt)


        print('- Création du fichier {} (!!! à compléter)'.format(sql_file_path.name))

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
        if not module_schema.sql_table_exists():
            return {}
        query, _ = module_schema.get_list({})
        modules_dict = module_schema.serialize_list(query.all())

        for module in modules_dict:
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
                module_file = SchemaMethods.load_json_file(file_path, load_keys=True)
                module_file['module_dir_path'] = str(file_path.parent)
                module_code = module_file['module']['module_code']
                module_files[module_code] = module_file

        return module_files

    @classmethod
    def modules(cls):
        return list(cls.modules_config().keys())

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
                module_config['module'][key] = module_config['module'].get(key, module_db[key])


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

    @classmethod
    def process_module_assets(cls, module_code):
        '''
            copie le dossier assets d'un module dans le repertoire static de geonature
            dans le dossier 'static/external_assets/modules/{module_code.lower()}'
        '''
        module_config = cls.module_config(module_code)
        module_assets_dir = Path(module_config['module_dir_path']) / 'assets'
        assets_static_dir = BACKEND_DIR / f'static/external_assets/modules/'
        assets_static_dir.mkdir(exist_ok=True, parents=True)

        symlink(
            module_assets_dir,
            assets_static_dir / module_code.lower(),
        )
