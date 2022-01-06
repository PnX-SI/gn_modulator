from ..schema import SchemaMethods
from sqlalchemy.orm.exc import NoResultFound


class ModuleBase():

    @classmethod
    def install_module(cls, module_name):

        # insert module in gn_commons.t_modules and gn_modules.t_module_complements
        cls.register_or_update_module(module_name)

        # process module data (nomenclature, groups ?, datasets, etc..)
        cls.process_module_sql(module_name)

        # process module data (nomenclature, groups ?, datasets, etc..)
        cls.process_module_data(module_name)
        return

    @classmethod
    def module_config(cls, module_name):
        return SchemaMethods.load_json_file_from_name(module_name)

    @classmethod
    def register_or_update_module(cls, module_name):

        schema_module = SchemaMethods('schemas.module.sous_module')
        module_data = cls.module_config(module_name)['module']
        module_code = module_data['module_code']
        module_row_data = {
            'module_label': module_data['module_label'],
            'module_desc': module_data['module_desc'],
            'module_picto': module_data['module_picto'],
            'active_frontend': module_data['active_frontend'],
            'module_code': module_code,
            'module_name': module_name,
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
    def module_code(cls, module_name):
        module_config = cls.module_config(module_name)
        return module_config['module']['module_code']

    @classmethod
    def save_sql_txt(cls, module_name, txt):

        module_path = SchemaMethods.file_path(module_name)
        sql_dir = module_path.parent / 'sql'
        sql_dir.mkdir(parents=True, exist_ok=True)
        sql_file_path = sql_dir / 'schema_{}.sql'.format(cls.module_code(module_name).lower())
        print('Sauvegarde du code sql dans {}'.format(sql_file_path))

        with open(sql_file_path, 'w') as f:
            f.write(txt)

    @classmethod
    def process_module_sql(cls, module_name):

        module_config = cls.module_config(module_name)
        schema_names = module_config['schemas']
        txt = ""
        for schema_name in schema_names:
            sm = SchemaMethods(schema_name)
            if sm.sql_schema_exists():
                return
            txt += sm.sql_txt_process()

        cls.save_sql_txt(module_name, txt)

        print('Exécution du code sql')
        SchemaMethods.c_sql_exec_txt(txt)
        pass

    @classmethod
    def process_module_data(cls, module_name):
        data_names = cls.module_config(module_name).get('data', [])
        infos = {}
        for data_name in data_names:
            infos[data_name] = SchemaMethods.process_data(data_name)
        pass
        SchemaMethods.log(SchemaMethods.txt_data_infos(infos))