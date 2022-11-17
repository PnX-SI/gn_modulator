"""
Test pour valider
- que les définition contenues dans le module sont valides
- les messages des remontées d'erreurs
"""

import pytest
from pathlib import Path
from gn_modules.definition import DefinitionMethods
from gn_modules.utils.cache import get_global_cache

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
        from gn_modules.blueprint import errors_init_module

        # pas d'erreurs à l'initialisation de gn_modules
        assert len(errors_init_module) == 0

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

        # json ok
        errors = DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_ok.json"
        )
        print(DefinitionMethods.errors_txt(errors))
        assert len(errors) == 0

        # yml ok
        errors = DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_ok.yml"
        )
        assert len(errors) == 0

        # json erreur de virgule
        errors_json_fail = DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail.json"
        )
        assert (
            errors_json_fail[0]["msg"]
            == "Erreur dans le fichier json: Expecting property name enclosed in double quotes: line 4 column 1 (char 42)"
        )

        # yml erreur yaml
        errors = DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail.yml"
        )
        assert len(errors) == 1

        # erreur 'pas de liste'
        errors = DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail_list.yml"
        )
        assert len(errors) == 1
        assert errors[0]["msg"] == "La définition ne doit pas être une liste"

        # erreur 'Ne correspond à aucun format de definition attendu'
        errors = DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail_format.yml"
        )
        assert len(errors) == 1
        assert errors[0]["msg"] == "Ne correspond à aucun format de definition attendu"

        # erreur déjà défini
        errors = DefinitionMethods.load_definition_file(
            definitions_test_dir / "load_definition_fail_existing.yml"
        )
        assert len(errors) == 1

        assert (
            "schema 'test.load_definition_ok' déjà défini(e) dans le fichier " in errors[0]["msg"]
        )

    def test_local_check_definition(self):
        """
        test sur l'utilisation et la remontée des erreurs
        de la méthode local_check_definition
        """

        # Test remontée des erreurs de validation d'un schema
        errors = DefinitionMethods.load_definition_file(
            definitions_test_dir / "local_check_definition_fail_type.yml"
        )
        assert len(errors) == 0

        errors = DefinitionMethods.local_check_definition(
            "schema", "test.test_local_check_fail_type"
        )
        assert len(errors) == 1
        assert (
            errors[0]["msg"]
            == "[properties.test] {'type_': 'string', 'title': 'test'} is not valid under any of the given schemas"
        )

    def test_global_check_definition(self):
        """
        test sur l'utilisation et la remontée des erreurs
        de la méthode global_check_definition et associées
        TODO
        """

        DefinitionMethods.load_definition_file(
            definitions_test_dir / "local_check_schema_names_fail.yml"
        )
        errors = DefinitionMethods.global_check_definition(
            "schema", "test.test_local_check_fail_schema_names"
        )

        print(DefinitionMethods.errors_txt(errors))

        assert len(errors) == 1

        assert (
            errors[0]["msg"]
            == "Le ou les schéma(s) 'schema.quinexistepas' ne sont pas présents dans les définitions existantes"
        )

    def test_template(self):
        """
        Tests sur ce que l'on attend d'un template
        """

        # si la definition du module m_monitoring_test
        # créé à partir du template m_monitoring.module_template
        # possède bien les éléments attendus

        definition = DefinitionMethods.get_definition("module", "m_monitoring_test")
        assert definition.get("pages") is not None
