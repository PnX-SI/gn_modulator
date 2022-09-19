from flask import current_app
from pathlib import Path
from . import errors
from ..schema import SchemaMethods
from flask_migrate import upgrade as db_upgrade, downgrade as db_downgrade
from sqlalchemy.orm.exc import NoResultFound

class ModuleCommands():

    @classmethod
    def remove_module(cls, module_code, force):

        print('Suppression du module {}'.format(module_code))

        try:
            module_config = cls.module_config(module_code)
        except errors.ModuleNotFound as e:
            print(e)
            return

        if not module_config['registred']:
            print("Le module n'est pas enregistré")

        # alembic
        db_downgrade(revision='{}@base'.format(module_code.lower()))

        #symlink
        cls.remove_migration_links(module_code)

        # suppression du module en base
        cls.delete_db_module(module_code)


    @classmethod
    def install_module(cls, module_code, force=False):

        print('Installation du module {}'.format(module_code))

        # mise en place des liens symboliques
        cls.make_migration_links(module_code)

        # alembic
        db_upgrade(revision='{}@head'.format(module_code.lower()))

        # pour les update du module ? # test si module existe
        cls.register_db_module(module_code)

        # process module data (nomenclature, groups ?, datasets, etc..)
        cls.process_module_data(module_code)

        # assets
        cls.process_module_assets(module_code)

        return

    @classmethod
    def init_module(cls, module_code, force):

        try:
            module_config = cls.module_config(module_code)

        except errors.ModuleNotFound as e:
            print(e)
            return

        if module_config['registred']:
            print("Le module {} est déjà enregistré".format(module_code))
            print("Pour reinitialiser le module, vous devez le supprimmer au préalable avec la commande suivante")
            print("geonature modules remove {}".format(module_code))
            return

        print('Initialisation du module {}'.format(module_code))

        cls.create_schema_sql(module_code, force)
        cls.create_reset_sql(module_code)

        migration_init_file_path = cls.migration_init_file_path(module_code)

        if not (migration_init_file_path and migration_init_file_path.exists()):
            cls.create_migration_init_file(module_code)
