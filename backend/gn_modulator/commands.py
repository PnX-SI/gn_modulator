"""
    MODULES commands

    init : initialize module (data/sql and migrations)
"""

import click
from flask.cli import with_appcontext

from gn_modulator import SchemaMethods, ModuleMethods, DefinitionMethods
from gn_modulator.imports.models import TImport
from gn_modulator.utils.errors import errors_txt
from gn_modulator import init_gn_modulator
from geonature.utils.env import db


@click.command("install")
@click.argument("module_code", required=False)
@click.option("-f", "--force", is_flag=True)
@with_appcontext
def cmd_install_module(module_code, force=False):
    """
    commande d'initialisation du module
    """

    init_gn_modulator()

    module_codes = ModuleMethods.module_codes()

    if module_code is None or module_code not in module_codes:
        print("registred", ModuleMethods.registred_modules())
        print("unregistred", ModuleMethods.unregistred_modules())
        print()

        if module_code:
            print(f"Le module demandé {module_code} n'existe pas.")
            print("Veuillez choisir un code parmi la liste suivante\n")

        for module_code in ModuleMethods.unregistred_modules():
            print(f"- {module_code}")

        print()
        print("Modules installés\n")
        for module_code in ModuleMethods.registred_modules():
            print(f"- {module_code}")

        print()

        return

    return ModuleMethods.install_module(module_code, force)


@click.command("remove")
@click.argument("module_code")
@click.option("-f", "--force", is_flag=True)
@with_appcontext
def cmd_remove_module(module_code, force=False):
    """
    commande d'initialisation du module
    """

    init_gn_modulator()

    return ModuleMethods.remove_module(module_code, force)


@click.command("update")
@with_appcontext
def cmd_update_modules():
    """
    commande d'initialisation du module
    """

    init_gn_modulator()

    return ModuleMethods.update_modules()


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

    init_gn_modulator()

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
    init_gn_modulator()
    txt = SchemaMethods(schema_code).doc_markdown()
    print(txt)
    return True


@click.command("import")
@click.option("-s", "schema_code")
@click.option("-d", "data_path", type=click.Path(exists=True))
@click.option(
    "-m",
    "--mapping",
    "mapping_file_path",
    type=click.Path(exists=True),
    help="chemin vers le script sql de pre-process",
)
@click.option(
    "-i",
    "--import-code",
    "import_code",
    help="code de l'import de ficher",
)
@click.option(
    "-v", "--verbose", type=int, default=1, help="1 : affiche les sortie, 2: les commandes sql  "
)
@with_appcontext
def cmd_import_bulk_data(
    schema_code=None, import_code=None, data_path=None, mapping_file_path=None, verbose=None
):
    """
    importe des données pour un schema
    """

    init_gn_modulator()

    if schema_code and data_path:
        impt = TImport(
            schema_code=schema_code, data_file_path=data_path, mapping_file_path=mapping_file_path
        )
        impt.process_import_schema()
        print(impt.pretty_infos())

    if import_code:
        TImport.process_import_code(import_code, data_path)

    return True


@click.command("features")
@click.argument("data_code", required=False)
@click.option("-v", "--verbose", is_flag=True, help="affiche les détails des feature")
def cmd_import_features(data_code=None, verbose=False):
    """
    importe des feature depuis un fichier (data) (.yml) referencé par la clé 'data_code'
    """

    init_gn_modulator()

    data_codes = sorted(DefinitionMethods.definition_codes_for_type("data"))

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

    init_gn_modulator()

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
    init_gn_modulator()

    print()
    print("Vérification des définitions de gn_modulator.\n")
    print(errors_txt())


@click.command("test")
def cmd_test():
    """
    test random
    """

    init_gn_modulator()

    from flask import current_app

    print("test", current_app)
    print(current_app.cli)
    # for key in dir(current_app):
    # print(key)


commands = [
    cmd_check,
    cmd_test,
    cmd_test_grammar,
    cmd_install_module,
    cmd_remove_module,
    cmd_update_modules,
    cmd_doc_schema,
    cmd_process_sql,
    cmd_import_features,
    cmd_import_bulk_data,
]
