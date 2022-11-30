"""
    MODULES commands

    init : initialize module (data/sql and migrations)
"""

import click
from flask.cli import with_appcontext

from gn_modules.schema import SchemaMethods
from gn_modules.module import ModuleMethods
from gn_modules.definition import DefinitionMethods
from gn_modules.utils.errors import errors_txt


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
@with_appcontext
def cmd_process_all(module_code):
    """ """

    ModuleMethods.remove_migration_links(module_code)
    ModuleMethods.make_migration_links(module_code)


@click.command("sql")
@click.option("-m", "module_code")
@click.option("-s", "schema_code")
@with_appcontext
def cmd_process_sql(module_code=None, schema_code=None, force=False):
    """
    affiche les commandes sql qui va être générées pour
    - un schema spécifié par l'option -s,schema_code
    - un module spécifié par l'option -s,module_code
        (ensemble de schema définis par le module)
    """

    if schema_code:
        sm = SchemaMethods(schema_code)
        txt, processed_schema_codes = sm.sql_txt_process()
        print(txt)

    if module_code:
        module_config = ModuleMethods.module_config(module_code)
        schema_codes = module_config["schemas"]
        processed_schema_codes = []
        txt_all = ""
        for schema_code in schema_codes:
            sm = SchemaMethods(schema_code)
            txt, processed_schema_codes = sm.sql_txt_process(processed_schema_codes)
            txt_all += txt
        print(txt)


@click.command("doc")
@click.argument("schema_code")
@click.option("-f", "--force", is_flag=True)
@with_appcontext
def cmd_doc_schema(schema_code, force=False):
    """
    affiche la doc d'un schema identifié par schema_code
    """

    txt = SchemaMethods(schema_code).doc_markdown()
    print(txt)
    return True


@click.command("import")
@click.option("-s", "schema_code")
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
    schema_code=None,
    import_file_path=None,
    data_file_path=None,
    pre_process_file_path=None,
    verbose=False,
    keep_raw=False,
):
    """
    importe des données pour un schema
    """

    if schema_code and data_file_path:
        SchemaMethods.process_csv_file(
            schema_code=schema_code,
            data_file_path=data_file_path,
            pre_process_file_path=pre_process_file_path,
            verbose=verbose,
            keep_raw=keep_raw,
        )

    if import_file_path:
        SchemaMethods.process_import_file(import_file_path, verbose)

    return True


@click.command("features")
@click.argument("data_code", required=False)
@click.option("-v", "--verbose", is_flag=True, help="affiche les détails des feature")
def cmd_import_features(data_code=None, verbose=False):
    """
    importe des feature depuis un fichier (data) (.yml) referencé par la clé 'data_code'
    """

    data_codes = sorted(DefinitionMethods.definition_codes("data"))

    if data_code is None or data_code not in data_codes:
        print()
        if data_code:
            print(f"La donnée demandée {data_code} n'existe pas.")
            print("Veuillez choisir un code parmi la liste suivante\n")
        for data_code in data_codes:
            print(f"- {data_code}")
            if verbose:
                data = DefinitionMethods.get_definition("data", data_code)
                print(f"    {data['title']}\n")
        if not verbose:
            print("\n(Utiliser -v pour voir les détails)\n")

        return

    data_codes = data_code.split(",")

    infos = {}
    for data_code in data_codes:
        print("import", data_code)
        infos[data_code] = SchemaMethods.process_features(data_code)

    SchemaMethods.log(SchemaMethods.txt_data_infos(infos))


@click.command("grammar")
@click.option("-s", "schema_code", help="Pour un schema donnée")
@click.option("-m", "module_code", help="Pour un module donné")
@click.option("-o", "object_code", help="Pour un module donné")
@click.option("-g", "grammar_type", help="Pour un type donnée (par ex 'un_nouveau_label")
def cmd_test_grammar(module_code=None, object_code=None, schema_code=None, grammar_type=None):
    """
    commande pour tester la grammaire
    - sans options
        affiche la grammaire pour tous les objects de tous les modules
    - schema_code
        pour un schema
    - module_code
        pour un module
    - module_code, object_code
        pour un object (il ne peux pas y avoir object_code sans module_code)
    - grammar_type
        pour un element précis de grammaire
    """

    try:
        grammar_txt = ModuleMethods.test_grammar(
            module_code, object_code, schema_code, grammar_type
        )

        print(f"\n{grammar_txt}")

    # cas schema non trouvé
    except SchemaMethods.errors.SchemaNotFoundError:
        print(f"\nErreur:\n  - Le schema {schema_code} n'a pas été trouvé.")

    # cas module non trouvé
    except ModuleMethods.errors.ModuleNotFoundError:
        print(f"\nErreur:\n  - Le module {module_code} n'a pas été trouvé.")

    # cas object sans module
    except ModuleMethods.errors.ModuleCodeRequiredError:
        print("\nErreur:")
        print(
            f"   - Il faut préciser un module_code (avec -m) afin d'accéder à la grammaire de l'object '{object_code}'."
        )

    # cas object non trouvé
    except ModuleMethods.errors.ModuleObjectNotFoundError:
        print(f"\nErreur:\n  - L'object {object_code} n'a pas été trouvé.")

    except SchemaMethods.errors.SchemaGrammarTypeError:
        print(f"\nErreur:\n  - Le type choisi '{grammar_type}' n'est pas valide.")
        print("    Veuillez choisir un type parmi la liste suivante : \n")

        for grammar_type in SchemaMethods.grammar_type_list():
            print(f"    - {grammar_type}")

    print()


@click.command("check")
def cmd_check():
    """
    - Initialise gn_module en chargeant et vérifiant les définitions
    - Collecte les erreurs rencontrées lors de l'initialisation
    - Affiche les erreurs rencontées
    """
    print()
    print("Vérification des définitions de gn_modules.\n")

    from gn_modules.blueprint import errors_init_module

    print(errors_txt())


commands = [
    cmd_check,
    cmd_test_grammar,
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
