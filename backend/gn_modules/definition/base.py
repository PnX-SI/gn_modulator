import os
from pathlib import Path
import yaml
import json
import jsonschema
from gn_modules.utils.env import config_directory
from gn_modules.utils.cache import set_global_cache, get_global_cache
from gn_modules.utils.errors import add_error, get_errors


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
    def definition_types(cls):
        """
        renvoie la liste des types de definitions
        """
        if get_global_cache(["definition_types"]) is None:
            set_global_cache(["definition_types"], [])
        return get_global_cache(["definition_types"], [])

    @classmethod
    def definition_codes(cls, definition_type):
        return list(get_global_cache([definition_type], {}).keys())

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
                lambda f: (f.endswith(".yml") or f.endswith(".json")),
                files,
            ):
                file_path = Path(root) / file
                cls.load_definition_file(file_path)

    @classmethod
    def check_references(cls):
        """
        Vérifie que les référence chargées sont valides
        """

        # test si les fichiers de référence ont bien été chargés
        for reference_code in cls.definition_codes("reference"):

            reference = cls.get_definition("reference", reference_code)
            try:
                jsonschema.Draft7Validator.check_schema(reference)
            except Exception as e:
                add_error(
                    definition_type="reference",
                    code="ERR_VALID_REF",
                    definition_code=reference_code,
                    msg=f"{str(e)}",
                )
                cls.remove_from_cache("reference", reference_code)
                continue

            if reference_code == "reference" or reference.get("id"):
                continue

            cls.local_check_definition("reference", reference_code)

    @classmethod
    def local_check_definition(cls, definition_type, definition_code):
        """
        Effectue les verification locales, ne concernant que la definition en question
        - conformité au jsonschema de référence
        -
        """
        definition = cls.get_definition(definition_type, definition_code)

        if definition is None:
            raise Exception(
                f" {definition_type} {definition_code} ne doit pas avoir une definition nulle"
            )

        cls.local_check_definition_reference(definition_type, definition_code)

        if definition_type in ["layout", "schema"]:
            cls.check_definition_dynamic_layout(definition_type, definition_code, definition)

        # suppression en cache de la definition si erreur locale
        if len(
            get_errors(
                definition_type=definition_type,
                definition_code=definition_code,
                error_code="ERR_LOCAL_CHECK",
            )
        ):
            cls.remove_from_cache(definition_type, definition_code)

    @classmethod
    def local_check_definition_reference(cls, definition_type, definition_code):
        """
        Verifie si la définition est valide par rapport
          à la référence jsonschema associée
        """

        definition = cls.get_definition(definition_type, definition_code)

        # schema de validation de la definition
        definition_reference_code = definition_type

        # patch schema_auto
        if definition_type == "schema" and definition["meta"].get("autoschema"):
            definition_reference_code = "schema_auto"

        definition_reference = cls.get_definition("reference", definition_reference_code)

        if definition_reference is None:

            add_error(
                definition_type=definition_type,
                definition_code=definition_code,
                code="ERR_LOCAL_CHECK_NO_REF_FOR_TYPE",
                msg=f"Une référence est requise pour valider pour le type {definition_type}",
            )
            return

        jsonschema_errors = jsonschema.Draft7Validator(definition_reference).iter_errors(
            definition
        )

        for error in jsonschema_errors:
            msg = error.message
            if error.path:
                msg = "[{}]\n    {}".format(".".join(str(x) for x in error.absolute_path), msg)

            add_error(
                definition_type=definition_type,
                definition_code=definition_code,
                code="ERR_LOCAL_CHECK_REF",
                msg=f"{msg}",
            )

    @classmethod
    def remove_from_cache(cls, definition_type, definition_code):
        del get_global_cache([definition_type])[definition_code]

    @classmethod
    def get_definition(cls, definition_type, definition_code):
        """
        retourne une définition pour un type et une clé donnés
        """

        return get_global_cache([definition_type, definition_code, "definition"])

    @classmethod
    def get_file_path(cls, definition_type, definition_code):
        """
        retourne le chemin du fichiern pour un type et une clé donnés
        """

        return get_global_cache([definition_type, definition_code, "file_path"])

    @classmethod
    def set_cache(cls, definition_type, definition_code, definition, file_path):
        """
        ajoute des données dans le cache
        - definition_type à definition_types, s'il n'y est pas déjà
        - la définiton
        - le chemin du fichier

        """
        if definition_type not in cls.definition_types():
            cls.definition_types().append(definition_type)
        set_global_cache([definition_type, definition_code, "definition"], definition)
        set_global_cache(
            [definition_type, definition_code, "file_path"],
            file_path,
        )

    @classmethod
    def local_check_definitions(cls):
        """
        Procède à la verification (locale) pour l'ensemble des definitions
        """

        # pour chaque type de definition sauf reférence qui sont validée en amont
        for definition_type in filter(
            lambda x: x not in ["reference", "template", "use_template"], cls.definition_types()
        ):
            # pour
            definition_codes = list(get_global_cache([definition_type], {}).keys())
            for definition_code in definition_codes:
                cls.local_check_definition(definition_type, definition_code)

    @classmethod
    def file_name(cls, definition):

        definition_type, definition_code = cls.get_definition_type_and_code(definition)

        return f"{definition_code}.{definition_type}"

    @classmethod
    def save_in_cache_definition(cls, definition, file_path):

        if isinstance(definition, list):
            add_error(
                definition_type="definition",
                file_path=str(file_path),
                msg="La définition ne doit pas être une liste",
                code="ERR_LOAD_LIST",
            )
            return

        if definition is None:
            add_error(
                definition_type="definition",
                file_path=str(file_path),
                msg="Le fichier est vide",
                code="ERR_DEF_EMPTY_FILE",
            )
            return

        definition_type, definition_code = cls.get_definition_type_and_code(definition)

        # si definition_type n'est pas défini
        # c'est que le type de configuration n'est pas detecté
        # tolérance pour les fichiers avec '-' ??
        if not definition_type:

            # fichiers avec '-' destinés à être inclu dans d'autres fichiers ??
            if "-" in file_path.stem:
                return

            add_error(
                definition_type="definition",
                file_path=str(file_path),
                msg="Ne correspond à aucun format de definition attendu",
                code="ERR_LOAD_UNKNOWN",
            )

        # test si la données n'existe pas dansun autre fichier
        # et déjà été chargée dans le cache
        # ce qui ne devrait pas être le cas
        elif cls.get_definition(definition_type, definition_code):
            add_error(
                definition_type=definition_type,
                definition_code=definition_code,
                file_path=str(file_path),
                msg=f"{definition_type} '{definition_code}' déjà défini(e) dans le fichier {cls.get_file_path(definition_type, definition_code)}",
                code="ERR_LOAD_EXISTING",
            )

        # check file_name
        # file_path = cls.get_file_path(definition_type, definition_code)
        # file_name = cls.file_name(definition)
        elif file_path.stem != cls.file_name(definition) and not (definition.get("use_template")):
            add_error(
                definition_type=definition_type,
                definition_code=definition_code,
                file_path=str(file_path),
                # msg=f"Le nom du fichier '{file_path.stem}{file_path.suffix}' doit se terminer en '.{definition_type}{file_path.suffix}'",
                msg=f"Le nom du fichier devrait être '{cls.file_name(definition)}{file_path.suffix}'",
                code="ERR_LOAD_FILE_NAME",
            )

        else:
            cls.set_cache(definition_type, definition_code, definition, file_path.resolve())

    @classmethod
    def load_definition_file(cls, file_path):

        # chargement du fichier yml
        try:
            definition = cls.load_definition_from_file(file_path)
            cls.save_in_cache_definition(definition, file_path)

            return definition
        # gestion des exceptions et récupération des erreur

        # - erreurs de format YAML
        except yaml.error.YAMLError as e:
            add_error(
                definition_type="definition",
                file_path=str(file_path),
                msg=f"Erreur dans le fichier yaml: {str(e)}",
                code="ERR_LOAD_YML",
            )

        # - erreurs de format JSON
        except json.JSONDecodeError as e:
            add_error(
                definition_type="definition",
                file_path=str(file_path),
                msg=f"Erreur dans le fichier json: {str(e)}",
                code="ERR_LOAD_JSON",
            )

    @classmethod
    def get_definition_type_and_code(
        cls,
        definition,
    ):
        """
        renvoie le type de definition et la clé pour le stockage dans le cache
        lorsque l'on peut en trouver une pour le dictionnaire de definition
        """

        if isinstance(definition, list):
            return None, None

        # patch définitions geometry
        if definition.get("id") is not None:
            return "reference", definition.get("id")

        # cas des références
        if definition.get("type") == "object":
            return "reference", definition.get("code")

        return definition.get("type"), definition.get("code")

    @classmethod
    def global_check_definitions(cls):
        """
        Véfifie les définitions de manière globale
        - on vérifie que les dépendances (schemas, module, layout) existent bien
        """

        # pour chaque type de definition sauf reférence qui sont validée en amont
        for definition_type in filter(lambda x: x != "reference", cls.definition_types()):
            # pour
            for definition_code in cls.definition_codes(definition_type):
                cls.global_check_definition(definition_type, definition_code)

    @classmethod
    def global_check_definition(cls, definition_type, definition_code):
        """
        - verification de la cohérence des 'schema_code'
        """

        definition = cls.get_definition(definition_type, definition_code)

        if definition is None:
            raise Exception("yakou!!", definition_type, definition_code)

        schema_codes = cls.definition_codes("schema")
        missing_schema_codes = cls.check_definition_element_in_list(
            definition, "schema_code", schema_codes
        )

        if missing_schema_codes:

            missings_schema_code_txt = ", ".join(map(lambda x: f"'{x}'", missing_schema_codes))
            add_error(
                definition_code=definition_code,
                definition_type=definition_type,
                code="ERR_GLOBAL_CHECK_MISSING_SCHEMA",
                msg=f"Le ou les schémas suivants ne sont pas présents dans les définitions : {missings_schema_code_txt}",
            )

        # dépendancies
        if dependencies := definition_type not in ["template", "use_template"] and definition.get(
            "dependencies"
        ):
            definition_codes = cls.definition_codes(definition_type)
            missing_dependencies = [
                dependency for dependency in dependencies if dependency not in definition_codes
            ]
            missing_dependencies_txt = ", ".join(missing_dependencies)
            if missing_dependencies:
                add_error(
                    definition_type=definition_type,
                    code="ERR_GLOBAL_CHECK_MISSING_DEPENDENCIES",
                    definition_code=definition_code,
                    msg=f"La ou les dépendances suivante de type {definition_type} ne sont pas présentent dans les définitions : {missing_dependencies_txt}",
                )

        # suppression en cache de la definition si erreur globale
        if len(
            get_errors(
                definition_type=definition_type,
                definition_code=definition_code,
                error_code="ERR_GLOBAL_CHECK_",
            )
        ):
            cls.remove_from_cache(definition_type, definition_code)

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

        # verification et application des templates
        cls.check_template_definitions()
        if get_errors():
            return

        cls.process_templates()
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
