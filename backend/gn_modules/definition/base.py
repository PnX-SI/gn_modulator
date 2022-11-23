import os
from pathlib import Path
import yaml
import json
import jsonschema
from gn_modules.utils.env import config_directory
from gn_modules.utils.cache import set_global_cache, get_global_cache
from gn_modules.utils.errors import add_error, get_errors

# liste de tous les type de definition
definition_types = [
    "schema",
    "reference",
    "data",
    "module",
    "import",
    "layout",
    "template",
]

# liste des types de definition avec une reference
# (un jsonschema qui permet de valider les definitions reçues)
# TODO ajouter tous les types sauf reference
required_references = ["schema", "schema_auto", "data", "import", "module"]
definition_types_with_reference = ["schema", "data", "import", "module"]


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
                cls.load_definition_file(file_path)

    @classmethod
    def check_references(cls):
        """
        Vérifie que les référence chargées sont valides
        """

        # Vérifier que les référence
        # qui vont servir dans la validation des définitions
        # ont bien été chargées
        # TODO rajouter module, layout dans required_references...
        for reference_key in required_references:
            if reference_key not in get_global_cache(["reference"]):
                add_error(
                    msg=f"La reférence {reference_key} n'a pas été trouvée", code="ERR_NO_REF"
                ),

        # test si les fichiers de référence ont bien été chargés
        for reference_key, reference in get_global_cache(["reference"]).items():

            try:
                jsonschema.Draft7Validator.check_schema(reference)
            except Exception as e:
                add_error(
                    type="reference",
                    code="ERR_VALID_REF",
                    key=reference_key,
                    msg=f"{str(e)}",
                )

    @classmethod
    def local_check_definition(cls, definition_type, definition_key):
        """
        Verifie la definition
        - si un json_schema est associé
        - TODO comment faire remonter des erreurs compréhensible ??
        """

        definition = cls.get_definition(definition_type, definition_key)

        # schema de validation de la definition
        definition_reference_name = cls.get_definition_reference_name(definition_type, definition)
        definition_reference = get_global_cache(
            ["reference", definition_reference_name, "definition"]
        )
        if definition_reference is None:

            if definition_type in definition_types_with_reference:
                add_error(
                    type=definition_type,
                    key=definition_key,
                    code="ERR_NO_REF_FOR_TYPE",
                    msg=f"Une référence est requise pour valider pour le type {definition_type}",
                )
            return

        resolver = jsonschema.RefResolver(
            base_uri="file://{}/".format(config_directory),
            referrer=definition_reference,
        )
        validator = jsonschema.Draft7Validator(definition_reference, resolver=resolver)
        jsonschema_errors = validator.iter_errors(definition)

        for error in jsonschema_errors:
            msg = error.message
            if error.path:
                msg = "[{}] {}".format(".".join(str(x) for x in error.absolute_path), msg)

            add_error(
                type=definition_type,
                key=definition_key,
                code="ERR_DEF_JS_VALID",
                msg=f"{msg}",
            )

    @classmethod
    def get_definition_reference_name(cls, definition_type, definition):
        """
        renvoie le schema de reference pour pouvoir valider une definition
        """

        # - schemas
        if definition_type == "schema":
            # deux possibilité (auto ou non)
            if definition["meta"].get("autoschema"):
                return "schema_auto"
            else:
                return "schema"

        # module
        if definition_type == "module":
            if definition.get("template"):
                return "module_with_template"
            else:
                return "module"

        if definition_type in ["data", "import"]:
            return definition_type

        return None

    @classmethod
    def get_definition(cls, definition_type, definition_key):
        """
        retourne une définition pour un type et une clé donnés
        """

        return get_global_cache([definition_type, definition_key, "definition"])

    @classmethod
    def get_file_path(cls, definition_type, definition_key):
        """
        retourne le chemin du fichiern pour un type et une clé donnés
        """

        return get_global_cache([definition_type, definition_key, "file_path"])

    @classmethod
    def set_cache(cls, definition_type, definition_key, definition, file_path):
        set_global_cache([definition_type, definition_key, "definition"], definition)
        set_global_cache(
            [definition_type, definition_key, "file_path"],
            file_path,
        )

    @classmethod
    def local_check_definitions(cls):
        """
        Procède à la verification (locale) pour l'ensemble des definitions
        """

        # pour chaque type de definition sauf reférence qui sont validée en amont
        for definition_type in filter(lambda x: x != "reference", definition_types):
            # pour
            for definition_key in get_global_cache([definition_type], {}).keys():
                cls.local_check_definition(definition_type, definition_key)

    @classmethod
    def save_in_cache_definition(cls, definition, file_path):

        if isinstance(definition, list):
            add_error(
                type="definition",
                file_path=str(file_path),
                msg="La définition ne doit pas être une liste",
                code="ERR_DEF_IS_LIST",
            )
            return

        if definition is None:
            add_error(
                type="definition",
                file_path=str(file_path),
                msg="Le fichier est vide",
                code="ERR_DEF_EMPTY_FILE",
            )
            return

        definition_type, definition_key = cls.get_definition_type_and_key(definition)

        # si global_cache_key n'est pas défini
        # c'est que letype de configuration n'est pas detecté
        if not definition_type:
            add_error(
                type="definition",
                file_path=str(file_path),
                msg="Ne correspond à aucun format de definition attendu",
                code="ERR_DEF_UNKNOWN",
            )

        # test si la données n'existe pas dansun autre fichier
        # et déjà été chargée dans le cache
        # ce qui ne devrait pas être le cas
        elif cls.get_definition(definition_type, definition_key):
            add_error(
                type=definition_type,
                file_path=str(file_path),
                msg=f"{definition_type} '{definition_key}' déjà défini(e) dans le fichier {cls.get_file_path(definition_type, definition_key)}",
                code="ERR_DEF_EXISTING",
            )

        # sinon
        # - verification des données
        # - mise en cache des definitions et du chemin du fichier
        else:
            cls.set_cache(definition_type, definition_key, definition, file_path.resolve())

    @classmethod
    def load_definition_file(cls, file_path):
        """ """

        # chargement du fichier yml
        try:
            definition = cls.load_definition_from_file(file_path, load_keys=True)

            cls.save_in_cache_definition(definition, file_path)

        # gestion des exceptions et récupération des erreur

        # - erreurs de format YAML
        except yaml.error.YAMLError as e:
            add_error(
                type="definition",
                file_path=str(file_path),
                msg=f"Erreur dans le fichier yaml: {str(e)}",
                code="ERR_DEF_YML",
            )

        # - erreurs de format JSON
        except json.JSONDecodeError as e:
            add_error(
                type="definition",
                file_path=str(file_path),
                msg=f"Erreur dans le fichier json: {str(e)}",
                code="ERR_DEF_JSON",
            )

    @classmethod
    def get_definition_type_and_key(
        cls,
        definition,
    ):
        """
        renvoie le type de definition et la clé pour le stockage dans le cache
        lorsque l'on peut en trouver une pour le dictionnaire de definition
        """

        # recherche du type de configuration
        template_name = definition.get("template", {}).get("name")
        # patch on veut juste assurer l'unicite de with_template_name
        with_template_name = definition.get("with_template") and json.dumps(
            definition.get("with_template"), sort_keys=True
        )
        schema_name = definition.get("meta", {}).get("schema_name")
        module_code = definition.get("module_code")
        layout_name = definition.get("layout_name")
        data_name = definition.get("data_name")
        import_name = definition.get("import_name")
        reference_id = definition.get("$id:")

        # assignation d'un type de definition et d'une reference
        definition_type, definition_key = (
            ("template", template_name)
            if template_name
            else ("with_template", with_template_name)
            if with_template_name
            else ("schema", schema_name)
            if schema_name
            else ("module", module_code)
            if module_code
            else ("layout", layout_name)
            if layout_name
            else ("data", data_name)
            if data_name
            else ("import", import_name)
            if import_name
            else ("reference", reference_id)
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

        # pour chaque type de definition sauf reférence qui sont validée en amont
        for definition_type in filter(lambda x: x != "reference", definition_types):
            # pour
            for definition_key in get_global_cache([definition_type], {}).keys():
                cls.global_check_definition(definition_type, definition_key)

    @classmethod
    def global_check_definition(cls, definition_type, definition_key):
        """
        - verification de la cohérence des 'schema_name'
        """

        definition = cls.get_definition(definition_type, definition_key)

        schema_names = cls.schema_names()
        missings_schema_name = cls.check_definition_element_in_list(
            definition, "schema_name", schema_names
        )

        if missings_schema_name:

            missings_schema_name_txt = ", ".join(map(lambda x: f"'{x}'", missings_schema_name))
            add_error(
                type=definition_type,
                code="ERR_DEF_MISSING_SCHEMA",
                msg=f"Le ou les schéma(s) {missings_schema_name_txt} ne sont pas présents dans les définitions existantes",
            )

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
        cls.load_definitions()
        if get_errors():
            return

        # verification des réferences
        # (qui vont servir à vérifier les definitions à l'étape suivante)
        cls.check_references()
        if get_errors():
            return

        # application des templates
        cls.process_definition_templates()
        if get_errors():
            return

        # vérification locale des définitions
        cls.local_check_definitions(),
        if get_errors():
            return

        # verification globale des definitions
        cls.global_check_definitions(),
        if get_errors():
            return

        return []
