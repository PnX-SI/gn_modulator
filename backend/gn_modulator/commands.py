"""
    MODULES commands

    init : initialize module (data/sql and migrations)
"""

import click
from flask.cli import with_appcontext

from gn_modulator import SchemaMethods, ModuleMethods, DefinitionMethods
from gn_modulator.imports.models import TImport
from gn_modulator.utils.errors import errors_txt
from gn_modulator import init_gn_modulator, get_errors
from geonature.utils.env import db


@click.command("install")
@click.argument("module_code", required=False)
@click.option("-f", "--force", is_flag=True)
@click.option("-p", "module_path", type=click.Path(exists=True))
@with_appcontext
def cmd_install_module(module_code=None, module_path=None, force=False):
    """
    commande d'initialisation du module
    """

    init_gn_modulator()

    module_codes = ModuleMethods.module_codes()

    if module_path or module_code in module_codes:
        return ModuleMethods.install_module(module_code, module_path, force)

    print("registred", ModuleMethods.registred_modules())
    print("unregistred", ModuleMethods.unregistred_modules())
    print()

    if module_code:
        print(f"Le module demandé {module_code} n'existe pas.")
        print("Veuillez choisir un code parmi la liste suivante\n")

    for unregistred_module_code in ModuleMethods.unregistred_modules():
        print(f"- {unregistred_module_code}")

    print()
    print("Modules installés\n")
    for registred_module_code in ModuleMethods.registred_modules():
        print(f"- {registred_module_code}")

    if module_code:
        raise Exception("Le module demandé {module_code} n'existe pas.")

    # return ModuleMethods.install_module(module_code, module_path, force)


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
@click.argument("doc_type")
@click.option("-e", "exclude")
@click.option("-f", "file_path", type=click.Path(exists=True))
@with_appcontext
def cmd_doc_schema(schema_code, doc_type, file_path=None, exclude=""):
    """
    affiche la doc d'un schema identifié par schema_code
    """
    init_gn_modulator()
    exclude_keys = exclude and exclude.split(",") or []
    txt = SchemaMethods(schema_code).doc_markdown(doc_type, exclude_keys, file_path)
    print(txt)
    return True


@click.command("import")
@click.option("-o", "object_code")
@click.option("-m", "module_code")
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
    module_code=None,
    object_code=None,
    import_code=None,
    data_path=None,
    mapping_file_path=None,
    verbose=None,
):
    """
    importe des données pour un schema
    """

    init_gn_modulator()

    if module_code and object_code and data_path:
        impt = TImport(
            module_code, object_code, data_file_path=data_path, mapping_file_path=mapping_file_path
        )
        impt.process_import_schema()
        print(impt.pretty_infos())

    if import_code:
        res = TImport.process_import_code(import_code, data_path)
        if res is None:
            print(f"L'import de code {import_code} n'existe pas\n")
            import_codes = sorted(DefinitionMethods.definition_codes_for_type("import"))
            print(f"Veuillez choisir parmi codes suivants\n")
            for import_code in import_codes:
                print(
                    f"- {import_code:>15} : {DefinitionMethods.get_definition('import', import_code)['title']}"
                )

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
    return not get_errors()


@click.command("test")
@click.option("-p", "module_path", type=click.Path(exists=True))
def cmd_test(module_path):
    """
    test random
    """

    import subprocess, importlib, site, sys, pkg_resources
    from geonature.utils.module import get_dist_from_code, iter_modules_dist
    from pathlib import Path

    subprocess.run(f"pip install -e '{module_path}'", shell=True, check=True)
    importlib.reload(site)
    for entry in sys.path:
        print(entry)
        pkg_resources.working_set.add_entry(entry)
    # load python package
    for module_dist in iter_modules_dist():
        path = Path(sys.modules[module_dist.entry_points["code"].module].__file__)
        if Path(module_path).resolve() in path.parents:
            module_code = module_dist.entry_points["code"].load()
            break
    print(module_path, module_code)
    return

    init_gn_modulator()

    a = importlib.reload(site)

    sm = SchemaMethods("m_sipaf.pf")
    sm.process_features("m_sipaf.pf_test", commit=False)
    params = {
        "fields": [
            "code_passage_faune",
            "actors.id_organism",
            "actors.id_role",
            "actors.role.nom_role",
            "actors.role.nom_complet",
        ],
        "filters": "code_passage_faune = TEST_SIPAF",
    }
    query = sm.query_list("m_sipaf", "R", params)
    print("\n\n", sm.format_sql(sm.sql_txt(query)))
    print("\n\nrequete\n\n")
    res = query.all()
    print("\n\nserial\n\n", params["fields"], "\n\n")
    res = sm.serialize_list(res, params["fields"])
    print(res)

    from flask import current_app


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
