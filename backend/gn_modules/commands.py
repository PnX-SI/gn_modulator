"""
    MODULES commands

    init : initialize module (data/sql and migrations)
"""

import click
from flask.cli import with_appcontext

from .schema import SchemaMethods
from .module import ModuleMethods

@click.command('init')
@click.argument('module_code')
@click.option('-f', '--force', is_flag=True)
@with_appcontext
def cmd_init_module(module_code, force=False):
    '''
        commande d'initialisation du module
    '''

    return ModuleMethods.init_module(module_code, force)

@click.command('install')
@click.argument('module_code')
@click.option('-f', '--force', is_flag=True)
@with_appcontext
def cmd_install_module(module_code, force=False):
    '''
        commande d'initialisation du module
    '''

    return ModuleMethods.install_module(module_code, force)


@click.command('remove')
@click.argument('module_code')
@click.option('-f', '--force', is_flag=True)
@with_appcontext
def cmd_remove_module(module_code, force=False):
    '''
        commande d'initialisation du module
    '''

    return ModuleMethods.remove_module(module_code, force)


@click.command('process_all')
@click.argument('module_code')
@click.option('-f', '--force', is_flag=True)
@with_appcontext
def cmd_process_all(module_code, force=False):
    '''

    '''

    ModuleMethods.remove_migration_links(module_code)
    ModuleMethods.make_migration_links(module_code)


@click.command('sql')
@click.argument('module_code')
@click.option('-f', '--force', is_flag=True)
@with_appcontext
def cmd_process_sql(module_code, force=False):
    '''
    '''

    ModuleMethods.create_schema_sql(module_code, force)

@click.command('doc')
@click.argument('schema_name')
@click.option('-f', '--force', is_flag=True)
@with_appcontext
def cmd_doc_schema(schema_name, force=False):
    '''
        affiche la doc d'un schema identifié par schema_name
    '''

    txt = SchemaMethods(schema_name).doc_markdown()
    print(txt)
    return True


@click.command('import')
@click.argument('schema_name')
@click.argument('data_file_path', type=click.Path(exists=True))
@click.option('-p', '--pre-process', 'pre_process_file_path', type=click.Path(exists=True), help="chemin vers le script sql de pre-process")
@click.option('-v', '--verbose', is_flag=True, help="affiche les commandes sql")
@with_appcontext
def cmd_import_bulk_data(schema_name, data_file_path, pre_process_file_path=None, verbose=False):
    '''
        importe des données pour un schema
    '''

    txt = SchemaMethods.process_csv_file(schema_name, data_file_path, pre_process_file_path, verbose)
    return True


commands = [
    cmd_init_module,
    cmd_install_module,
    cmd_remove_module,
    cmd_doc_schema,
    cmd_process_all,
    cmd_process_sql,
    cmd_import_bulk_data
]
