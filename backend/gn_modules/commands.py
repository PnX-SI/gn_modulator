"""
    MODULES commands

    init : initialize module (data/sql and migrations)
"""

import click
from flask.cli import with_appcontext
from flask_marshmallow import Schema

from .schema import SchemaMethods
from .module import ModuleMethods
from .schema import errors
from gn_modules import module

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


commands = [
    cmd_init_module,
    cmd_install_module,
    cmd_remove_module,
    cmd_doc_schema
]
