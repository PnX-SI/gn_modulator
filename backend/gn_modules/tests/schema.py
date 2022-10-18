import pytest  # noqa
from gn_modules.schema import SchemaMethods


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCommons:
    def test_load_definitions(self):
        """
        Test de chargement des schemas
        """

        SchemaMethods.init_schemas_definitions()
        assert 1 == 1

    def test_load_schemas(self):
        """
        Test de chargement des schemas
        """

        SchemaMethods.init_schemas_models_and_serializers()
        assert 1 == 1
