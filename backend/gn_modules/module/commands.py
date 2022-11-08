from . import errors
from ..schema import SchemaMethods
from flask_migrate import upgrade as db_upgrade, downgrade as db_downgrade
from geonature.utils.env import db


class ModuleCommands:
    @classmethod
    def remove_module(cls, module_code, force=False):

        try:
            module_config = cls.module_config(module_code)
        except errors.ModuleNotFoundError as e:
            print(e)
            return

        if not module_config["registred"]:
            print("Le module n'est pas enregistré")

        print("Suppression du module {}".format(module_code))

        # suppression des modules depandant du module en cours
        module_deps_installed = [
            module_dep_code
            for module_dep_code, module_child_config in cls.modules_config().items()
            if (
                module_code in module_child_config.get("dependencies", [])
                and module_child_config["registred"]
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
            return

        for module_dep_code in module_deps_installed:
            cls.remove_module(module_dep_code, force)

        # alembic
        db.session.commit()  # pour eviter les locks ???

        if cls.migration_files(module_code):
            db_downgrade(revision=f"{module_code.lower()}@base")

        # suppression du module en base
        print("- suppression du module {} en base".format(module_code))

        cls.delete_db_module(module_code)

        # symlink
        cls.remove_migration_links(module_code)

    @classmethod
    def install_module(cls, module_code, force=False):

        print("Installation du module {}".format(module_code))

        # test si les dépendances sont installées
        module_config = cls.module_config(module_code)
        for module_dep_code in module_config.get("dependencies", []):
            module_dep_config = cls.module_config(module_dep_code)
            if not module_dep_config["registred"]:
                if not force:
                    print(
                        f"Le module {module_code} depend du module {module_dep_code} qui n'est pas installé"
                    )
                    print("Vous pouvez")
                    print(
                        f"    - soit installer le module {module_dep_code} au préalable,"
                    )
                    print(
                        "    - soit relancer la commande avec l'option -f (--force) pour permettre l'installation automatique des dépendances"
                    )
                    return
                cls.install_module(module_dep_code, force)

        # mise en place des liens symboliques
        cls.make_migration_links(module_code)

        # alembic
        # - test if migration file(s) exist(s)
        if cls.migration_files(module_code):
            db.session.commit()  # pour eviter les locks ???
            db_upgrade(revision=f"{module_code.lower()}@head")

        # pour les update du module ? # test si module existe
        cls.register_db_module(module_code)

        # process module data (nomenclature, groups ?, datasets, etc..)
        SchemaMethods.reinit_marshmallow_schemas()
        cls.process_module_features(module_code)

        # assets
        cls.process_module_assets(module_code)

        return

    @classmethod
    def init_module(cls, module_code, force):

        try:
            module_config = cls.module_config(module_code)

        except errors.ModuleNotFoundError as e:
            print(e)
            return

        if module_config["registred"]:
            print("Le module {} est déjà enregistré".format(module_code))
            print(
                "Pour reinitialiser le module, vous devez le supprimmer au préalable avec la commande suivante"
            )
            print("geonature modules remove {}".format(module_code))
            return

        print("Initialisation du module {}".format(module_code))

        cls.create_schema_sql(module_code, force)
        cls.create_reset_sql(module_code)

        migration_init_file_path = cls.migration_init_file_path(module_code)

        if not (migration_init_file_path and migration_init_file_path.exists()):
            cls.create_migration_init_file(module_code)
