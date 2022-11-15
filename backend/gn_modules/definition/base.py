import os
from pathlib import Path
import yaml
import json
import jsonschema
from gn_modules.schema import SchemaMethods
from gn_modules.utils.env import config_directory
from gn_modules.utils.cache import set_global_cache, get_global_cache

# liste de tous les type de definition
definition_types = ["schema", "reference", "data", "module", "import", "layout"]

# liste des types de definition avec une reference
# (un jsonschema qui permet de valider les definitions reçues)
# TODO ajouter tous les types sauf reference
required_references = ["schema", "schema_auto", "data", "import"]
definition_types_with_reference = ["schema", "data", "import"]


class DefinitionBase:
    """
    Méthodes qui permettent de charger, verifier et traiter les definitions pour
    - les schemas
        - méthodes modèles, sérialisation, api, verification de données etc..)
    - les modules
        - choix des api à ouvrir avec les droit associé au module
        - hierarchie du frontend, definition des pages
    - les données
        - feature à ajouter à l'installation du module
        - peut être optionnel (données d'exemple)
    """

    @classmethod
    def schema_names(cls):
        return list(get_global_cache(["schema"], {}).keys())

    @classmethod
    def module_codes(cls):
        return list(get_global_cache(["module"], {}).keys())

    @classmethod
    def layout_names(cls):
        return list(get_global_cache(["layout"], {}).keys())

    @classmethod
    def reference_names(cls):
        return list(get_global_cache(["reference"], {}).keys())

    @classmethod
    def load_definitions(cls):
        """
        Cette méthode permet
        - de parcourir l'ens

        emble des fichiers de configuration yml
        - de charger et mettre en cache les définitions pour
            - les modules
            - les schemas
            - les layout
            - les données(features, data ?)

        renvoie la liste des erreurs
        """

        definitions_errors = []

        # boucle sur les fichiers yml contenus dans le dossier de gn_modules
        # on charge les definitions et on les mets en cache
        for root, dirs, files in os.walk(config_directory, followlinks=True):
            # on filtre sur
            # - les fichiers yml
            # - qui ne contiennent pas '-' dans le nom du fichier
            #     - dans ce cas c'est une partie du fichier de config,
            #     - par exemple
            #       - site-propertie.yml contient la clé 'properties' du dictionnaire de definition de site
            for file in filter(
                lambda f: (f.endswith(".yml") or f.endswith(".json")) and "-" not in f,
                files,
            ):
                file_path = Path(root) / file
                definitions_errors += cls.load_definition_file(file_path)

        return definitions_errors

    @classmethod
    def check_references(cls):
        """
        Vérifie que les référence chargées sont valides
        """

        check_references_errors = []

        # Vérifier que les référence
        # qui vont servir dans la validation des définitions
        # ont bien été chargées
        # TODO rajouter module, layout dans required_references...
        for reference_key in required_references:
            if reference_key not in get_global_cache(["reference"]):
                check_references_errors.append(
                    {
                        "type": "reference",
                        "msg": f"La reférence {reference_key} n'a pas été trouvée",
                    }
                )

        # test si les fichiers de référence ont bien été chargés
        for reference_key, reference in get_global_cache(["reference"]).items():

            try:
                jsonschema.Draft7Validator.check_schema(reference)
            except Exception as e:
                check_references_errors.append(
                    {
                        "type": "reference",
                        "file_path": get_global_cache(
                            ["reference", reference_key, "file_path"]
                        ),
                        "definition": reference,
                        "msg": f"{str(e)}",
                    }
                )

        return check_references_errors

    @classmethod
    def local_check_definition(cls, definition_type, definition_key):
        """
        Verifie la definition
        - si un json_schema est associé
        - TODO comment faire remonter des erreurs compréhensible ??
        """

        check_local_definition_errors = []

        definition = get_global_cache([definition_type, definition_key, "definition"])

        # schema de validation de la definition
        definition_reference = cls.get_definition_reference(definition_type, definition)

        if definition_reference is None:
            if definition_type in definition_types_with_reference:
                raise Exception(f"{definition_type}: pas de reference trouvee")
            return check_local_definition_errors

        resolver = jsonschema.RefResolver(
            base_uri="file://{}/".format(config_directory),
            referrer=definition_reference,
        )
        validator = jsonschema.Draft7Validator(definition_reference, resolver=resolver)
        jsonschema_errors = validator.iter_errors(definition)

        for error in jsonschema_errors:
            msg = error.message
            if error.path:
                msg = "[{}] {}".format(
                    ".".join(str(x) for x in error.absolute_path), msg
                )

            check_local_definition_errors.append(
                {
                    "type": definition_type,
                    "file_path": get_global_cache(
                        [definition_type, definition_key, "file_path"]
                    ),
                    "definition": definition,
                    "msg": f"{msg}",
                }
            )

        return check_local_definition_errors

    @classmethod
    def get_definition_reference(cls, definition_type, definition):
        """
        renvoie le schema de reference pour pouvoir valider une definition
        """

        # - schemas
        if definition_type == "schema":
            # deux possibilité (auto ou non)
            if definition["meta"].get("autoschema"):
                return get_global_cache(["reference", "schema_auto", "definition"])
            else:
                return get_global_cache(["reference", "schema", "definition"])

        # TODO
        # - module, layout

        # - data
        if definition_type in ["data", "import"]:
            return get_global_cache(["reference", definition_type, "definition"])

        return None

    @classmethod
    def local_check_definitions(cls):
        """
        Procède à la verification (locale) pour l'ensemble des definitions
        """

        local_check_definitions_errors = []

        # pour chaque type de definition sauf reférence qui sont validée en amont
        for definition_type in filter(lambda x: x != "reference", definition_types):
            # pour
            for definition_key in get_global_cache([definition_type], {}).keys():
                local_check_definitions_errors += cls.local_check_definition(
                    definition_type, definition_key
                )

        return local_check_definitions_errors

    @classmethod
    def load_definition_file(cls, file_path):
        """ """

        definition_errors = []

        # chargement du fichier yml
        try:
            definition = cls.load_definition_from_file(file_path, load_keys=True)

            # resolution des élément commençant par '_'
            # et contenus dans _defs
            # (sauf les element dynamique qui com,mencent par __f__)
            definition = cls.process_defs(definition)

            if isinstance(definition, list):
                definition_errors.append(
                    {
                        "type": "definition",
                        "file_path": str(file_path),
                        "msg": "La definition ne doit pas être une liste",
                    }
                )
                return definition_errors

            definition_type, definition_key = cls.get_definition_type_and_key(
                definition, file_path
            )

            # si global_cache_key n'est pas défini
            # c'est que letype de configuration n'est pas detecté
            if not definition_type:
                definition_errors.append(
                    {
                        "type": "definition",
                        "file_path": str(file_path),
                        "definition": definition,
                        "msg": "Ne correspond à aucun format de definition attendu",
                    }
                )

            # test si la données n'existe pas dansun autre fichier
            # et déjà été chargée dans le cache
            # ce qui ne devrait pas être le cas
            elif get_global_cache([definition_type, definition_key]):
                definition_errors.append(
                    {
                        "type": definition_type,
                        "file_path": str(file_path),
                        "definition": definition,
                        "msg": f"{definition_type} '{definition_key}' déjà défini(e) dans le fichier {get_global_cache([definition_type, definition_key, 'file_path'])}",
                    }
                )

            # sinon
            # - verification des données
            # - mise en cache des definitions et du chemin du fichier
            else:
                set_global_cache(
                    [definition_type, definition_key, "definition"], definition
                )
                set_global_cache(
                    [definition_type, definition_key, "file_path"], file_path
                )

        # gestion des exceptions et récupération des erreur

        # - erreurs de format YAML
        except yaml.error.YAMLError as e:
            definition_errors.append(
                {
                    "type": "definition",
                    "file_path": str(file_path),
                    "msg": f"Erreur dans le fichier yaml: {str(e)}",
                }
            )

        # - erreurs de format JSON
        except json.JSONDecodeError as e:
            definition_errors.append(
                {
                    "type": "definition",
                    "file_path": str(file_path),
                    "msg": f"Erreur dans le fichier json: {str(e)}",
                }
            )

        # - erreurs dans les _defs et les élements commençant par '_'
        except cls.errors.DefinitionNoDefsError as e:
            definition_errors.append(
                {"type": "definition", "file_path": str(file_path), "msg": f"{str(e)}"}
            )

        return definition_errors

    @classmethod
    def get_definition_type_and_key(cls, definition, file_path):
        """
        renvoie le type de definition et la clé pour le stockage dans le cache
        lorsque l'on peut en trouver une pour le dictionnaire de definition
        """

        # recherche du type de configuration
        schema_name = definition.get("meta", {}).get("schema_name")
        module_code = definition.get("module", {}).get("module_code")
        layout_name = definition.get("layout_name")
        data_name = definition.get("data_name")
        import_name = definition.get("import_name")
        reference_id = (
            definition.get("$id:") or definition.get("$id") or definition.get("$schema")
        )

        # assignation d'un type de definition et d'une reference
        definition_type, definition_key = (
            ("schema", schema_name)
            if schema_name
            else ("module", module_code)
            if module_code
            else ("layout", layout_name)
            if layout_name
            else ("data", data_name)
            if data_name
            else ("import", import_name)
            if import_name
            else ("reference", file_path.stem)
            if reference_id
            else (None, None)
        )

        return definition_type, definition_key

    @classmethod
    def global_check_definitions(cls):
        """
        Véfifie les définitions de manière globale
        - on vérifie que les dépendances (schemas, module, layout) existent bien
        """

        global_check_definitions_errors = []

        # pour chaque type de definition sauf reférence qui sont validée en amont
        for definition_type in filter(lambda x: x != "reference", definition_types):
            # pour
            for definition_key in get_global_cache([definition_type], {}).keys():
                global_check_definitions_errors += cls.global_check_definition(
                    definition_type, definition_key
                )

        return global_check_definitions_errors

    @classmethod
    def global_check_definition(cls, definition_type, definition_key):
        """
        - verification de la cohérence des 'schema_name'
        """

        global_check_definition_errors = []

        definition = get_global_cache([definition_type, definition_key, "definition"])
        schema_names = cls.schema_names()
        missings_schema_name = cls.check_definition_element_in_list(
            definition, "schema_name", schema_names
        )

        if missings_schema_name:

            global_check_definition_errors.append(
                {
                    "file_path": get_global_cache(
                        [definition_type, definition_key, "file_path"]
                    ),
                    "msg": f"Les schémas {', '.join(missings_schema_name)} ne sont pas présents dans les définitions existantes",
                }
            )

        return global_check_definition_errors

    @classmethod
    def init_definitions(cls):
        """
        fonction principale qui va charger, verifier et traiter les definition
        en controlant bien qu'à chaque étape il n'y ai pas d'erreurs

        retourne les erreur rencontrée lors de l'initialisation
        lorsque des erreurs sont remontée, on ne passe pas à l'étape suivante
        l'initialisation est considérée comme valide lorsque la liste d'erreur est vide
        """

        # chargement des définitions
        init_definitions_errors = cls.load_definitions()
        if len(init_definitions_errors):
            return init_definitions_errors

        # verification des reference
        # (qui vont servir à vérifier les definitions à l'étape suivante)
        init_definitions_errors = cls.check_references()
        if len(init_definitions_errors):
            return init_definitions_errors

        # vérification locale des définitions
        init_definitions_errors = cls.local_check_definitions()
        if len(init_definitions_errors):
            return init_definitions_errors

        # verification globale des definitions
        init_definitions_errors = cls.global_check_definitions()
        if len(init_definitions_errors):
            return init_definitions_errors

        return init_definitions_errors
