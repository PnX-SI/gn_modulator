import subprocess
import pkg_resources
import importlib
import sys
import site
from pathlib import Path

from flask_migrate import upgrade as db_upgrade, downgrade as db_downgrade
from geonature.utils.module import get_dist_from_code, iter_modules_dist
from geonature.utils.env import db
from gn_modulator.utils.files import symlink
from gn_modulator.utils.env import config_dir
from gn_modulator import SchemaMethods, DefinitionMethods
from . import errors


class ModuleCommands:
    @classmethod
    def update_modules(cls):
        for module_code in cls.module_codes():
            module_config = cls.module_config(module_code)
            if not (module_config.get("registred") and cls.is_python_module(module_code)):
                continue

            cmd_pip_install = f"pip install -e '{cls.module_path(module_code)}'"
            print(cmd_pip_install)
            subprocess.run(cmd_pip_install, shell=True, check=True)
            importlib.reload(site)
            for entry in sys.path:
                pkg_resources.working_set.add_entry(entry)
            get_dist_from_code(module_code)

    @classmethod
    def remove_module(cls, module_code, force=False):
        """
        Supprime un module et ses dépendances
        """
        try:
            module_config = cls.module_config(module_code)
        except cls.errors.ModuleNotFoundError as e:
            print(e)
            return False

        if not module_config["registred"]:
            print("Le module n'est pas enregistré")

        print(f"Suppression du module {module_code}")

        # suppression des modules depandant du module en cours
        module_deps_installed = [
            module_dep_code
            for module_dep_code in cls.module_codes()
            if (
                module_code in cls.module_config(module_dep_code).get("dependencies", [])
                and cls.module_config(module_dep_code).get("registred")
            )
        ]

        if module_deps_installed and not force:
            print(
                f"Il y a des modules installés qui dependent du module à supprimer {module_code}"
            )

            ("- " + ", ".join(module_deps_installed))
            print(f"Afin de pouvoir supprimer le module {module_code} vous pouvez")
            print("  - soit supprimer au préalable des modules ci dessus")
            print(
                "  - ou bien relancer la commande avec l'options -f (--force) pour supprimer automatiquement les modules dépendants"
            )
            return False

        for module_dep_code in module_deps_installed:
            cls.remove_module(module_dep_code, force)

        if cls.is_python_module(module_code):
            # alembic
            db.session.commit()  # pour eviter les locks ???

            # TODO comment savoir s'il y a une migration
            module_dist = get_dist_from_code(module_code)
            if module_dist.entry_points.select(name="migrations"):
                db_downgrade(revision=f"{module_code.lower()}@base")

        # suppression du module en base
        print(f"- suppression du module {module_code} en base")

        cls.delete_db_module(module_code)

        # suppression de la config

        if (config_dir() / module_code).is_dir():
            (config_dir() / module_code).unlink()
        # unregister
        module_config["registred"] = False

        if cls.is_python_module(module_code):
            subprocess.run(f"pip uninstall -y {module_code}", shell=True, check=True)

        return True

    @classmethod
    def install_module(cls, module_code=None, module_path=None, force=False):
        module_path = module_path and Path(module_path)
        if module_path:
            subprocess.run(f"pip install -e '{module_path}'", shell=True, check=True)

            importlib.reload(site)
            for module_dist in iter_modules_dist():
                module = module_dist.entry_points["code"].module
                if module not in sys.modules:
                    path = Path(importlib.import_module(module).__file__)
                else:
                    path = Path(sys.modules[module].__file__)
                if module_path.resolve() in path.parents:
                    module_code = module_dist.entry_points["code"].load()
                    break

            module_dist = get_dist_from_code(module_code)
            if module_dist.entry_points.select(name="migrations"):
                db.session.commit()  # pour eviter les locks ???
                db_upgrade(revision=f"{module_code.lower()}@head")

            symlink((module_path / "config").resolve(), (config_dir() / module_code))

            DefinitionMethods.load_definitions()
            SchemaMethods.init_schemas()
            cls.init_module_config(module_code)
            # ModuleMethods.init_modules()

        print(f"Installation du module {module_code}")

        # si module_path

        # install module
        # symlink config

        # reload definitions

        # test si les dépendances sont installées
        module_config = cls.module_config(module_code)
        for module_dep_code in module_config.get("dependencies", []):
            module_dep_config = cls.module_config(module_dep_code)
            if not module_dep_config.get("registred"):
                if not force:
                    print(
                        f"Le module {module_code} depend du module {module_dep_code} qui n'est pas installé"
                    )
                    print("Vous pouvez")
                    print(f"    - soit installer le module {module_dep_code} au préalable,")
                    print(
                        "    - soit relancer la commande avec l'option -f (--force) pour permettre l'installation automatique des dépendances"
                    )
                    return False
                cls.install_module(module_dep_code, force)

        # pour les update du module ? # test si module existe
        cls.register_db_module(module_code)

        # process module data (nomenclature, groups ?, datasets, etc..)
        SchemaMethods.reinit_marshmallow_schemas()
        cls.process_module_features(module_code)

        # register
        module_config["registred"] = True

        return True

    @classmethod
    def test_grammar(cls, module_code=None, object_code=None, schema_code=None, grammar_type=None):
        """
        renvoie un tecte contenant les élément de grammaire des schemas concerné par les argument
        (par defaut tout)
        """

        # tests
        if module_code:
            cls.module_config(module_code)

        if object_code and not module_code:
            raise errors.ModuleCodeRequiredError("")

        if object_code and module_code:
            cls.object_config(module_code, object_code)

        grammar_type_list = SchemaMethods.grammar_type_list()

        if grammar_type and grammar_type not in grammar_type_list:
            raise SchemaMethods.errors.SchemaGrammarTypeError(
                f"Le type de grammaire choisi {grammar_type} n'est pas valide."
            )

        # récupération de grammar list
        grammar_list = []

        # si schema_code on traite seulement ce schéma
        if schema_code:
            sm = SchemaMethods(schema_code)
            grammar_list.append(sm.config_display())

        else:
            modules_config = cls.modules_config()

            # si module_code est défini on ne prend que celui là
            for module_code_loop in filter(
                lambda key: not (module_code and key != module_code), modules_config
            ):
                module_config = modules_config[module_code_loop]

                # si object_code est défini on ne prend que celui là
                for object_code_loop in filter(
                    lambda key: not (object_code and key != object_code),
                    module_config.get("objects", {}),
                ):
                    object_config = module_config["objects"][object_code_loop]

                    current_grammar_item = object_config["display"]

                    # pour eviter les doublons
                    existing_items = None
                    existing_items = [
                        grammar_item
                        for grammar_item in grammar_list
                        if current_grammar_item["label"] == grammar_item["label"]
                    ]
                    if not existing_items:
                        grammar_list.append(current_grammar_item)

        if not grammar_list:
            return ""

        # tri de grammar_list selon les labels par ordre alphabétique
        grammar_list.sort(key=lambda x: x["label"])

        # passer grammar_list en texte
        # par exemple
        #
        #  - le_label
        #    - le gite
        #    - l'éolienne, etc...

        grammar_txt = ""

        # si grammar_type est défini, on ne prend que celui la
        for grammar_type_loop in filter(
            lambda key: not (grammar_type and grammar_type != key) and key != "description",
            grammar_list[0],
        ):
            grammar_txt += f"- {grammar_type_loop}\n"

            for grammar_item in grammar_list:
                grammar_txt += f"  - {grammar_item[grammar_type_loop]}\n"

            grammar_txt += "\n"

        return grammar_txt
