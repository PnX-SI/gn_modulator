"""
    MODULES commands

    init : initialize module (data/sql and migrations)
"""

import click
from flask.cli import with_appcontext

from .schema import SchemaMethods
from .module import ModuleMethods


@click.command("init")
@click.argument("module_code")
@click.option("-f", "--force", is_flag=True)
@click.option("-r", "--reinstall", is_flag=True)
@with_appcontext
def cmd_init_module(module_code, force=False, reinstall=False):
    """
    commande d'initialisation du module
    """

    ModuleMethods.init_module(module_code, force)


@click.command("install")
@click.argument("module_code")
@click.option("-f", "--force", is_flag=True)
@with_appcontext
def cmd_install_module(module_code, force=False):
    """
    commande d'initialisation du module
    """

    return ModuleMethods.install_module(module_code, force)


@click.command("remove")
@click.argument("module_code")
@click.option("-f", "--force", is_flag=True)
@with_appcontext
def cmd_remove_module(module_code, force=False):
    """
    commande d'initialisation du module
    """

    return ModuleMethods.remove_module(module_code, force)


@click.command("process_all")
@click.argument("module_code")
@click.option("-f", "--force", is_flag=True)
@with_appcontext
def cmd_process_all(module_code, force=False):
    """ """

    ModuleMethods.remove_migration_links(module_code)
    ModuleMethods.make_migration_links(module_code)


@click.command("sql")
@click.option("-m", "module_code")
@click.option("-s", "schema_name")
@with_appcontext
def cmd_process_sql(module_code=None, schema_name=None, force=False):
    """
    affiche les commandes sql qui va être générées pour
    - un schema spécifié par l'option -s,schema_name
    - un module spécifié par l'option -s,module_code
        (ensemble de schema définis par le module)
    """

    if schema_name:
        sm = SchemaMethods(schema_name)
        txt, processed_schema_names = sm.sql_txt_process()
        print(txt)

    if module_code:
        module_config = ModuleMethods.module_config(module_code)
        schema_names = module_config["schemas"]
        processed_schema_names = []
        txt_all = ""
        for schema_name in schema_names:
            sm = SchemaMethods(schema_name)
            txt, processed_schema_names = sm.sql_txt_process(processed_schema_names)
            txt_all += txt
        print(txt)


@click.command("doc")
@click.argument("schema_name")
@click.option("-f", "--force", is_flag=True)
@with_appcontext
def cmd_doc_schema(schema_name, force=False):
    """
    affiche la doc d'un schema identifié par schema_name
    """

    txt = SchemaMethods(schema_name).doc_markdown()
    print(txt)
    return True


@click.command("import")
@click.option("-s", "schema_name")
@click.option("-d", "data_file_path", type=click.Path(exists=True))
@click.option(
    "-p",
    "--pre-process",
    "pre_process_file_path",
    type=click.Path(exists=True),
    help="chemin vers le script sql de pre-process",
)
@click.option(
    "-i",
    "--import-file",
    "import_file_path",
    type=click.Path(exists=True),
    help="chemin vers le fichier json d'imports",
)
@click.option("-v", "--verbose", is_flag=True, help="affiche les commandes sql")
@click.option("-k", "--keep-raw", is_flag=True, help="garde le csv en base")
@with_appcontext
def cmd_import_bulk_data(
    schema_name=None,
    import_file_path=None,
    data_file_path=None,
    pre_process_file_path=None,
    verbose=False,
    keep_raw=False,
):
    """
    importe des données pour un schema
    """

    if schema_name and data_file_path:
        SchemaMethods.process_csv_file(
            schema_name=schema_name,
            data_file_path=data_file_path,
            pre_process_file_path=pre_process_file_path,
            verbose=verbose,
            keep_raw=keep_raw,
        )

    if import_file_path:
        SchemaMethods.process_import_file(import_file_path, verbose)

    return True


@click.command("features")
@click.argument("data_name")
def cmd_import_features(data_name):
    """
    importe des feature depuis un fichier (data) (.yml) referencé par la clé 'data_name'
    """

    data_names = data_name.split(",")

    infos = {}
    for data_name in data_names:
        print("import", data_name)
        infos[data_name] = SchemaMethods.process_features(data_name)

    SchemaMethods.log(SchemaMethods.txt_data_infos(infos))


commands = [
    cmd_init_module,
    # cmd_reinit_module,
    cmd_install_module,
    cmd_remove_module,
    cmd_doc_schema,
    cmd_process_all,
    cmd_process_sql,
    cmd_import_features,
    cmd_import_bulk_data,
]
