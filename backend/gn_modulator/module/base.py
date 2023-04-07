from pathlib import Path
from sqlalchemy.orm.exc import NoResultFound
from gn_modulator.utils.env import assets_dir, migrations_directory
from gn_modulator.utils.files import symlink
from gn_modulator.schema import SchemaMethods
from gn_modulator.utils.cache import get_global_cache
from gn_modulator.definition import DefinitionMethods
from gn_modulator import MODULE_CODE


class ModuleBase:
    @classmethod
    def add_actions(cls, module_code, object_code, actions):
        object_config = cls.object_config(module_code, object_code)
        for action in actions:
            if action not in object_config["cruved"]:
                object_config["cruved"] = (object_config["cruved"] or "") + action

    @classmethod
    def is_python_module(cls, module_code):
        """
        Test si on a un fichier setup.py pour ce sous_module
        """

        setup_file_path = cls.module_path(module_code) / "setup.py"
        return setup_file_path.exists()

    @classmethod
    def module_path(cls, module_code):
        return DefinitionMethods.get_file_path("module", module_code).parent

    @classmethod
    def module_codes(cls):
        """
        Renvoie la liste des code de module présents dans les fichiers de config
        """

        module_codes = []

        for module_code in DefinitionMethods.definition_codes_for_type("module"):
            definition = DefinitionMethods.get_definition("module", module_code)
            if DefinitionMethods.get_unresolved_template_params(definition):
                continue
            module_codes.append(module_code)

        return module_codes

    @classmethod
    def registred_modules(cls):
        """
        liste des modules installés
        """
        return list(
            filter(
                lambda module_code: cls.module_config(module_code)["registred"],
                cls.module_codes(),
            )
        )

    @classmethod
    def unregistred_modules(cls):
        """
        liste des modules non installés
        """
        return list(
            filter(
                lambda module_code: not cls.module_config(module_code)["registred"],
                cls.module_codes(),
            )
        )

    @classmethod
    def migrations_dir(cls, module_code=None):
        if not module_code:
            return migrations_directory
        return cls.module_dir_path(module_code) / "migrations"

    @classmethod
    def module_dir_path(cls, module_code):
        return Path(get_global_cache(["module", module_code, "file_path"]).parent)

    @classmethod
    def register_db_module(cls, module_code):
        print(f"- Enregistrement du module {module_code}")
        schema_module = SchemaMethods("commons.module")
        module_config = cls.module_config(module_code)
        module_row_data = {
            "module_code": module_code,
            "module_label": module_config["module"]["module_label"],
            "module_desc": module_config["module"]["module_desc"],
            "module_picto": module_config["module"]["module_picto"],
            "active_frontend": module_config["module"].get("active_frontend") or False,
            "module_path": f"{MODULE_CODE.lower()}/{module_code.lower()}",
            "active_backend": False,
        }
        try:
            schema_module.update_row(module_code, module_row_data, field_name="module_code")
        except NoResultFound:
            schema_module.insert_row(module_row_data)

    @classmethod
    def delete_db_module(cls, module_code):
        schema_module = SchemaMethods("commons.module")
        schema_module.delete_row(module_code, field_name="module_code", params={})

    @classmethod
    def create_schema_sql(cls, module_code, force=False):
        module_config = cls.module_config(module_code)
        schema_codes = module_config["schemas"]

        txt = ""

        processed_schema_codes = []
        for schema_code in schema_codes:
            sm = SchemaMethods(schema_code)
            txt_schema, processed_schema_codes = sm.sql_txt_process(processed_schema_codes)
            txt += txt_schema

        sql_file_path = cls.migrations_dir(module_code) / "data/schema.sql"
        if sql_file_path.exists() and not force:
            print("- Le fichier existe déjà {}".format(sql_file_path))
            print("- Veuillez relancer la commande avec -f pour forcer la réécriture")
            return
        sql_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sql_file_path, "w") as f:
            f.write(txt)
        print("- Création du fichier {}".format(sql_file_path.name))

    @classmethod
    def process_module_features(cls, module_code):
        module_config = cls.module_config(module_code)
        data_codes = module_config.get("features", [])

        if not data_codes:
            return

        print("- Ajout de données depuis les features")

        for data_code in data_codes:
            infos = {}
            infos[data_code] = SchemaMethods.process_features(data_code)

        SchemaMethods.log(SchemaMethods.txt_data_infos(infos))

    @classmethod
    def process_module_assets(cls, module_code):
        """
        copie le dossier assets d'un module dans le repertoire media de geonature
        dans le dossier 'media/modulator/assets/{module_code.lower()}'
        """

        if module_code == MODULE_CODE:
            return []

        module_assets_dir = Path(cls.module_dir_path(module_code)) / "assets"
        module_img_path = Path(module_assets_dir / "module.jpg")

        # on teste si le fichier assets/module.jpg est bien présent
        if not module_img_path.exists():
            return [
                {
                    "file_path": module_img_path.resolve(),
                    "msg": f"Le fichier de l'image du module {module_code} n'existe pas",
                }
            ]

        # s'il y a bien une image du module,
        #   - on crée le lien des assets vers le dossize static de geonature
        assets_dir().mkdir(exist_ok=True, parents=True)
        symlink(
            module_assets_dir,
            assets_dir() / module_code.lower(),
        )

        return []

    @classmethod
    def test_module_dependencies(cls, module_code):
        """
        test si les modules dont dépend un module sont installés
        """

        module_config = cls.module_config(module_code)

        dependencies = module_config.get("dependencies", [])
        db_installed_modules = cls.modules_config_db()

        test_dependencies = True

        for dep in dependencies:
            if db_installed_modules.get(dep) is None:
                print(dep, db_installed_modules.keys())
                print("-- Dependance(s) manquantes")
                print(f"  - module '{dep}'")
                test_dependencies = False

        return test_dependencies
