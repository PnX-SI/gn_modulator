from ast import mod
from datetime import datetime
from uuid import uuid4
from flask import current_app
from pathlib import Path
import os
from ..schema import SchemaMethods
from jinja2 import Template

class ModuleMigration():

    @classmethod
    def migration_init_file_path(cls, module_code, revision_id=None):
        '''
            renvoie le nom du fichier de la première migration (dont le nom contient 'init_{module_code}')
        '''

        suffix = 'init_{}.py'.format(module_code.lower())

        if revision_id:
            return cls.migrations_dir(module_code) / 'versions/{}_{}'.format(revision_id, suffix)
        for root, dir, files in os.walk(cls.migrations_dir(module_code) / 'versions'):
            for f in files:
                if f.endswith(suffix):
                    return Path(root) / f
        return None

    @classmethod
    def generate_revision_id(cls):
        return uuid4().hex[-12:]

    @classmethod
    def migration_files(cls, module_code, link=False, types=[]):
        migration_files=[]
        suffix = '_{}.py'.format(module_code.lower())
        dir_path = (
            cls.migrations_dir() / 'versions' if link
            else cls.migrations_dir(module_code) / 'versions'
        )
        for root, dir, files in os.walk(dir_path):
            for f in files:
                if f.endswith(suffix) and (not types or [t for t in types if '_{}_'.format(t) in f]):
                    migration_files.append(Path(root) / f)
            break
        return migration_files

    @classmethod
    def make_migration_links(cls, module_code):

        # liens symboliques des fichier de migration
        for f in cls.migration_files(module_code, link=False):
            f_link = cls.migrations_dir() / 'versions' / f.name
            if f_link.exists():
                f_link.unlink()
            f_link.symlink_to(f)

        # liens symboliques des fichier sql
        data_dir = cls.migrations_dir(module_code) / 'data'
        data_link = cls.migrations_dir() / 'data' / module_code.lower()

        if data_link.exists():
            data_link.unlink()

        data_link.symlink_to(data_dir)

        print("- Création des liens symboliques vers 'gn_modules/migrations' (data et versions)")

    @classmethod
    def remove_migration_links(cls, module_code):

        for f in cls.migration_files(module_code, link=True):
            f.unlink()

        data_link = cls.migrations_dir() / 'data' / module_code.lower()
        if data_link.exists():
            data_link.unlink()

        print("- Suppression des liens symboliques")


    @classmethod
    def remove_migration_files(cls, module_code):
        for f in cls.migration_files(module_code, link=False, types=['rev', 'init']):
            f.unlink()


    @classmethod
    def create_migration_init_file(cls, module_code):
        template_file_path = cls.migrations_dir() / 'templates/init.py.sample'
        with open(template_file_path) as template_file:
            template = Template(template_file.read())
            revision_id = cls.generate_revision_id()
            template_data = {
                'module_code': module_code,
                'revision_id': revision_id,
                'revision_date': datetime.now()
            }
            txt = template.render(template_data)

            migration_init_file_path = cls.migration_init_file_path(module_code, revision_id)
            migration_init_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(migration_init_file_path, 'w') as revision_file:
                revision_file.write(txt)
            print('- Création du fichier de migration initial : {}'.format(migration_init_file_path.name))