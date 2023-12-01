"""
Test pour valider
- que les définition contenues dans le module sont valides
- les messages des remontées d'erreurs

reste à tester (a minima)
ERR_DEF_EMPTY_FILE
"""

import pytest
from gn_modulator.definition import DefinitionMethods
from gn_modulator.utils.cache import get_global_cache
from gn_modulator.utils.errors import get_errors, clear_errors
from gn_modulator.utils.env import definitions_test_dir
from .utils.definition import (
    test_load_definition,
    test_local_check_definition,
    test_global_check_definition,
    test_process_template,
)


@pytest.mark.usefixtures(scope="session")
class TestDefinitions:
    def test_init_gn_module(self):
        """
        On teste si l'initialisation du module s'est bien déroulée
        - s'il n'y a pas d'erreur dans les définitions
        - si on a bien des schemas, modules et layout à minima
        - si le traitement de ces définition n'entraîne par d'erreurs
        """
        # pas d'erreurs à l'initialisation de gn_modulator
        assert (
            len(get_errors()) == 0
        ), "Il ne doit pas y avoir d'erreur à ce stade (initialisation module)"

        # on a bien chargé des schemas, modules, layouts
        assert len(DefinitionMethods.definition_codes_for_type("reference")) > 0
        assert len(DefinitionMethods.definition_codes_for_type("module")) > 0
        assert len(DefinitionMethods.definition_codes_for_type("layout")) > 0
        assert len(DefinitionMethods.definition_codes_for_type("schema")) > 0

        # on a bien les références
        # - pour les définitions
        for reference_key in ["schema", "module"]:
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

    def test_check_references(self):
        """
        test si le schema de validation est valide (selon la référence de schemas de validation)
        """
        clear_errors()

        test_load_definition(definitions_test_dir / "check_references_fail.reference.yml")
        DefinitionMethods.check_references()

        assert (
            len(get_errors()) == 1
        ), f"check references, on s'attend à voir remonter une erreur (et non {len(get_errors())})"
        get_errors()[0]["error_code"] == "ERR_VALID_REF"

    def test_load_definition_json_ok(self):
        # load json ok
        test_load_definition(definitions_test_dir / "load_definition_json_ok.schema.json")
        DefinitionMethods.remove_from_cache("schema", "load_definition_json_ok")

    def test_load_definition_yml_ok(self):
        # load yml ok
        test_load_definition(definitions_test_dir / "load_definition_yml_ok.schema.yml")
        DefinitionMethods.remove_from_cache("schema", "load_definition_yml_ok")

    def test_load_definition_json_fail(self):
        # load json fail

        test_load_definition(definitions_test_dir / "load_definition_fail.json", "ERR_LOAD_JSON")

    def test_load_definition_yml_fail(self):
        # load yml fail
        test_load_definition(definitions_test_dir / "load_definition_fail.yml", "ERR_LOAD_YML")

    def test_load_definition_list_fail(self):
        # load list fail
        test_load_definition(
            definitions_test_dir / "load_definition_list_fail.yml", "ERR_LOAD_LIST"
        )

    def test_load_definition_unknown_fail(self):
        # load unknown fail
        test_load_definition(
            definitions_test_dir / "load_definition_unknown_fail.yml",
            "ERR_LOAD_UNKNOWN",
        )

    def test_load_definition_existing_fail(self):
        # load existing fail
        test_load_definition(definitions_test_dir / "load_definition_existing_fail.schema.yml")

        test_load_definition(
            definitions_test_dir / "load_definition_existing_fail.schema.yml",
            "ERR_LOAD_EXISTING",
        )
        DefinitionMethods.remove_from_cache("schema", "load_definition_existing_fail")

    def test_load_definition_file_name_fail(self):
        # ERR_LOAD_FILE_NAME
        test_load_definition(
            definitions_test_dir / "load_definition_file_name_fail.layout.yml",
            "ERR_LOAD_FILE_NAME",
        )

    def test_local_check_definition_dynamic(self):
        """
        test de remontée des erreur de validation des layout pour les éléments dynamiques
        ERR_LOCAL_CHECK_DYNAMIC
        """

        test_local_check_definition(
            definitions_test_dir / "local_check_definition_dyn_fail.layout.yml",
            "ERR_LOCAL_CHECK_DYNAMIC",
        )

    def test_local_check_definition_no_ref_for_type(self):
        """
        ERR_LOCAL_CHECK_NO_REF_FOR_TYPE
        """

        test_local_check_definition(
            definitions_test_dir / "local_check_definition_no_ref_for_type_fail.gloubi.yml",
            "ERR_LOCAL_CHECK_NO_REF_FOR_TYPE",
        )

    def test_local_check_auto_model_not_found(self):
        """
        ERR_LOCAL_CHECK_AUTO_MODEL_NOT_FOUND
        """

        test_local_check_definition(
            definitions_test_dir / "local_check_auto_model_not_found.schema.yml",
            "ERR_LOCAL_CHECK_AUTO_MODEL_NOT_FOUND",
        )

    def test_global_check_definition_missing_schema(self):
        """
        test global pour vérifier la remontée de missing schema
        """
        test_global_check_definition(
            definitions_test_dir / "global_check_schema_codes_fail.schema.yml",
            "ERR_GLOBAL_CHECK_MISSING_SCHEMA",
        )

    def test_global_check_definition_missing_dependencies(self):
        """
        test global pour vérifier la remontée de missing schema
        """
        test_global_check_definition(
            definitions_test_dir / "global_check_dependencies_fail.data.yml",
            "ERR_GLOBAL_CHECK_MISSING_DEPENDENCIES",
        )

    def test_template_not_found_fail(self):
        """
        ERR_TEMPLATE_NOT_FOUND
        """

        test_process_template(
            definitions_test_dir / "process_template_not_found_fail.layout.yml",
            "ERR_TEMPLATE_NOT_FOUND",
        )

    def test_template_unresolved_fields_fail(self):
        """
        ERR_TEMPLATE_UNRESOLVED_FIELDS
        """

        test_load_definition(
            definitions_test_dir / "process_template_unresolved_fields_fail_template.layout.yml"
        )
        test_process_template(
            definitions_test_dir / "process_template_unresolved_fields_fail.layout.yml",
            "ERR_TEMPLATE_UNRESOLVED_FIELDS",
        )

    def test_template(self):
        """
        Tests sur ce que l'on attend d'un template
        """

        clear_errors()

        # si la definition du module m_monitoring_test
        # créé à partir du template m_monitoring.module
        # possède bien les éléments attendus

        definition = DefinitionMethods.get_definition("module", "m_monitoring_test_1")

        if definition is None:
            return
        # assert definition.get("pages_definition") is not None

        assert definition["code"] == "m_monitoring_test_1"
