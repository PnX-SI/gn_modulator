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

# répertoire contenant les definitions destinées aux test
definitions_test_dir = Path(__file__).parent / "definitions_test"


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

    def test_load_definition(self):
        """
        tests sur le chargement des fichiers yml
        et sur la remontée des erreurs
        lors de l'utilisation de la methode DefinitionMethods.load_definition_file
        """

        clear_errors()

        # json ok
        DefinitionMethods.load_definition_file(definitions_test_dir / "load_definition_ok.json")
        assert len(get_errors()) == 0

        # yml ok
        DefinitionMethods.load_definition_file(definitions_test_dir / "load_definition_ok.yml")
        assert len(get_errors()) == 0

        # json erreur de virgule
        DefinitionMethods.load_definition_file(definitions_test_dir / "load_definition_fail.json")
        assert len(get_errors()) == 1
        assert get_errors()[0]["code"] == "ERR_DEF_JSON"

        clear_errors()
        assert len(get_errors()) == 0

        # yml erreur yaml
        DefinitionMethods.load_definition_file(definitions_test_dir / "load_definition_fail.yml")
        assert len(get_errors()) == 1
        assert get_errors()[0]["code"] == "ERR_DEF_YML"

        clear_errors()

        # erreur 'pas de liste'
        DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail_list.yml"
        )
        print(errors_txt())
        assert len(get_errors()) == 1
        assert get_errors()[0]["code"] == "ERR_DEF_IS_LIST"
        clear_errors()

        # erreur 'Ne correspond à aucun format de definition attendu'
        DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail_format.yml"
        )
        assert len(get_errors()) == 1
        assert get_errors()[0]["code"] == "ERR_DEF_UNKNOWN"
        clear_errors()

        # erreur déjà défini
        DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail_existing.yml"
        )
        assert len(get_errors()) == 1
        assert get_errors()[0]["code"] == "ERR_DEF_EXISTING"
        clear_errors()

    def test_local_check_definition(self):
        """
        test sur l'utilisation et la remontée des erreurs
        de la méthode local_check_definition
        """

        clear_errors()

        # Test remontée des erreurs de validation d'un schema
        DefinitionMethods.load_definition_file(
            definitions_test_dir / "local_check_definition_fail_type.yml"
        )
        assert len(get_errors()) == 0

        DefinitionMethods.local_check_definition("schema", "test.test_local_check_fail_type")
        assert len(get_errors()) == 1
        assert get_errors()[0]["code"] == "ERR_DEF_JS_VALID"
        clear_errors()

    def test_global_check_definition(self):
        """
        test sur l'utilisation et la remontée des erreurs
        de la méthode global_check_definition et associées
        TODO
        """

        clear_errors()

        DefinitionMethods.load_definition_file(
            definitions_test_dir / "local_check_schema_names_fail.yml"
        )
        DefinitionMethods.global_check_definition(
            "schema", "test.test_local_check_fail_schema_names"
        )

        assert len(get_errors()) == 1

        assert get_errors()[0]["code"] == "ERR_DEF_MISSING_SCHEMA"
        clear_errors()

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
