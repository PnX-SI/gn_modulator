"""
Test pour valider
- que les définition contenues dans le module sont valides
- les messages des remontées d'erreurs
"""

import pytest
from pathlib import Path
from gn_modules.definition import DefinitionMethods
from gn_modules.utils.cache import get_global_cache
from gn_modules.utils.errors import get_errors, clear_errors, errors_txt
from gn_modules.utils.env import definitions_test_dir

# répertoire contenant les definitions destinées aux test

"""
err code
TODO
    ERR_VALID_REF
    ERR_NO_REF_FOR_TYPE
    ERR_DEF_EMPTY_FILE
    ERR_TEMPLATE_NO_NAME
    ERR_TEMPLATE_NOT_FOUND
    ERR_TEMPLATE_UNRESOLVED_FIELDS

DONE
    ERR_GLOBAL_MISSING_SCHEMA
    ERR_LOAD_YML
    ERR_LOAD_JSON
    ERR_LOAD_EXISTING
    ERR_LOAD_UNKNOWN
    ERR_LOCAL_CHECK_REF
    ERR_LOAD_LIST
"""


@pytest.mark.usefixtures(scope="session")
class TestDefinitions:
    def test_init_gn_module(self):
        """
        On teste si l'initialisation du module s'est bien déroulée
        - s'il n'y a pas d'erreur dans les définitions
        - si on a bien des schemas, modules et layout à minima
        - si le traitement de ces définition n'entraîne par d'erreurs
        """

        # pas d'erreurs à l'initialisation de gn_modules
        assert len(get_errors()) == 0

        # on a bien chargé des schemas, modules, layouts
        assert len(DefinitionMethods.reference_names()) > 0
        assert len(DefinitionMethods.module_codes()) > 0
        assert len(DefinitionMethods.layout_names()) > 0

        # on a bien les références
        # - pour les définitions
        for reference_key in ["schema", "schema_auto", "import", "module"]:
            assert get_global_cache(["reference", reference_key]) is not None

        # - pour la validation
        for reference_key in [
            "geometry",
            "linestring",
            "multilinestring",
            "multipolygon",
            "point",
            "polygon",
        ]:
            assert get_global_cache(["reference", reference_key]) is not None

    def test_load_definition(self, file_path=None, error_code=None):
        """
        tests sur le chargement des fichiers yml
        et sur la remontée des erreurs
        lors de l'utilisation de la methode DefinitionMethods.load_definition_file
        """

        clear_errors()

        if file_path is None:
            return

        definition = DefinitionMethods.load_definition_file(file_path)

        # s'il n'y pas d'erreur de code
        # on s'assure que le chargement du fichier s'est bien passé
        if error_code is None:
            assert len(get_errors()) == 0
            assert definition is not None
            definition_type, definition_key = DefinitionMethods.get_definition_type_and_key(
                definition
            )
            assert definition_type is not None
            assert definition_key is not None

            return definition

        assert get_errors()[0]["code"] == error_code

        return definition

    def test_local_check_definition(self, file_path=None, error_code=None):
        """
        test sur l'utilisation et la remontée des erreurs
        de la méthode local_check_definition
        """

        clear_errors()

        if file_path is None:
            return

        # chargment de la definition (+ test que tout est ok)
        definition = self.test_load_definition(file_path)

        definition_type, definition_key = DefinitionMethods.get_definition_type_and_key(definition)

        DefinitionMethods.local_check_definition(definition_type, definition_key)

        # si le code d'erreur n'est pas défini, on s'assure qu'il n'y a pas d'erreur
        if error_code is None:
            assert len(get_errors()) == 0
            return definition

        assert len(get_errors()) == 1

        # on teste si le code de l'erreur est celui attendu
        assert get_errors()[0]["code"] == error_code

        # on teste si la definition a bien été supprimé
        assert get_global_cache([definition_type, definition_key]) is None

        return definition

    def test_global_check_definition(self, file_path=None, error_code=None):
        """
        test sur l'utilisation et la remontée des erreurs
        de la méthode global_check_definition et associées
        TODO
        """

        if not file_path:
            return

        clear_errors()

        definition = self.test_local_check_definition(file_path)

        defintion_type, definition_key = DefinitionMethods.get_definition_type_and_key(definition)

        DefinitionMethods.global_check_definition(defintion_type, definition_key)

        # si error_code n'est pas renseigné, on s'attend à n'avoir aucune erreur
        if error_code is None:
            assert len(get_errors()) == 0
            return definition

        # test si on a bien le code d'erreur attendu
        assert get_errors()[0]["code"] == error_code

        # test si file_path est bien renseigné
        assert get_errors()[0].get("file_path") is not None

        # test si la definition a bien été retirée du cache
        assert get_global_cache([defintion_type, definition_key]) is None

        clear_errors()

    def test_load_definition_json_ok(self):
        # load json ok
        return self.test_load_definition(definitions_test_dir / "load_definition_ok.json")

    def test_load_definition_yml_ok(self):
        # load yml ok
        return self.test_load_definition(definitions_test_dir / "load_definition_ok.yml")

    def test_load_definition_json_fail(self):
        # load json fail
        return self.test_load_definition(
            definitions_test_dir / "load_definition_fail.json", "ERR_LOAD_JSON"
        )

    def test_load_definition_yml_fail(self):
        # load yml fail
        return self.test_load_definition(
            definitions_test_dir / "load_definition_fail.yml", "ERR_LOAD_YML"
        )

    def test_load_definition_list_fail(self):
        # load list fail
        return self.test_load_definition(
            definitions_test_dir / "load_definition_list_fail.yml", "ERR_LOAD_LIST"
        )

    def test_load_definition_unknown_fail(self):
        # load unknown fail
        return self.test_load_definition(
            definitions_test_dir / "load_definition_unknown_fail.yml", "ERR_LOAD_UNKNOWN"
        )

    def test_load_definition_existing_fail(self):
        # load existing fail
        return self.test_load_definition(
            definitions_test_dir / "load_definition_existing_fail.yml", "ERR_LOAD_EXISTING"
        )

    def test_local_check_definition_ref_fail(self):
        """
        test de remontée des erreur de validation par le schema de refence avec jsonschema
        """

        return self.test_local_check_definition(
            definitions_test_dir / "local_check_definition_ref_fail.yml", "ERR_LOCAL_CHECK_REF"
        )

    def test_global_check_definition_missing_schema(self):
        """
        test global pour vérifier la remontée de missing schema
        """
        return self.test_global_check_definition(
            definitions_test_dir / "global_check_schema_names_fail.yml",
            "ERR_GLOBAL_MISSING_SCHEMA",
        )

    def test_global_check_definition_missing_dependencies(self):
        """
        test global pour vérifier la remontée de missing schema
        """
        return self.test_global_check_definition(
            definitions_test_dir / "global_check_dependencies_fail.yml",
            "ERR_GLOBAL_MISSING_DEPENDENCIES",
        )

    def test_template(self):
        """
        Tests sur ce que l'on attend d'un template
        """

        clear_errors()

        # si la definition du module m_monitoring_test
        # créé à partir du template m_monitoring.module_template
        # possède bien les éléments attendus

        definition = DefinitionMethods.get_definition("module", "m_monitoring_test_1")
        assert definition.get("pages") is not None

        assert definition["module_code"] == "m_monitoring_test_1"
