import subprocess
import pkg_resources
import importlib
import sys
import site

from flask_migrate import upgrade as db_upgrade, downgrade as db_downgrade
from geonature.utils.module import get_dist_from_code, module_db_upgrade
from geonature.utils.env import db
from gn_modulator import SchemaMethods, DefinitionMethods
from . import errors


class ModuleCommands:
    @classmethod
    def remove_module(cls, module_code, force=False):
        try:
            module_config = cls.module_config(module_code)
        except cls.errors.ModuleNotFoundError as e:
            print(e)
            return False

        if not module_config["registred"]:
            print("Le module n'est pas enregistré")

        print("Suppression du module {}".format(module_code))

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
            print("- " + ", ".join(module_deps_installed))
            print(f"Afin de pouvoir supprimer le module {module_code} vous pouvez")
            print("  - soit supprimer au préalable des modules ci dessus")
            print(
                "  - ou bien relancer la commande avec l'options -f (--force) pour supprimer automatiquement les modules dépendants"
            )
            return False

        for module_dep_code in module_deps_installed:
            cls.remove_module(module_dep_code, force)

        module_path = DefinitionMethods.get_file_path("module", module_code).parent
        setup_file_path = module_path / "setup.py"
        if setup_file_path.exists():
            # alembic
            db.session.commit()  # pour eviter les locks ???

            # TODO comment savoir s'il y a une migration
            module_dist = get_dist_from_code(module_code)
            if "migrations" in module_dist.get_entry_map("gn_module"):
                db_downgrade(revision=f"{module_code.lower()}@base")

        # suppression du module en base
        print("- suppression du module {} en base".format(module_code))

        cls.delete_db_module(module_code)

        # unregister
        module_config["registred"] = False

        if setup_file_path.exists():
            subprocess.run(f"pip remove {module_code}", shell=True, check=True)

        return True

    @classmethod
    def install_module(cls, module_code, force=False):
        print("Installation du module {}".format(module_code))

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

        # si on a un setup.py on installe le module python
        module_path = DefinitionMethods.get_file_path("module", module_code).parent
        setup_file_path = module_path / "setup.py"
        if setup_file_path.exists():
            subprocess.run(f"pip install -e '{module_path}'", shell=True, check=True)
            importlib.reload(site)
            for entry in sys.path:
                pkg_resources.working_set.add_entry(entry)

            # load python package
            module_dist = get_dist_from_code(module_code)
            if "migrations" in module_dist.get_entry_map("gn_module"):
                db.session.commit()  # pour eviter les locks ???
                db_upgrade(revision=f"{module_code.lower()}@head")

        # pour les update du module ? # test si module existe
        cls.register_db_module(module_code)

        # process module data (nomenclature, groups ?, datasets, etc..)
        SchemaMethods.reinit_marshmallow_schemas()
        cls.process_module_features(module_code)

        # assets
        cls.process_module_assets(module_code)

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
