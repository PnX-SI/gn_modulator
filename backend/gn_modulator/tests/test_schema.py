import pytest  # noqa
from gn_modulator.schema import SchemaMethods


@pytest.mark.usefixtures(scope="session")
class TestSchemas:
    def test_backrefs(self):
        """
        Test sur les backrefs
            - exemple site: modules(backref=sites)
        """

        sm = SchemaMethods("commons.module")
        # on verifie que le modèle et le sérialiser possèdent un attribut 'sites'
        assert hasattr(sm.Model(), "sites")
        assert "sites" in sm.MarshmallowSchema()._declared_fields.keys()


# @pytest.mark.usefixtures("client_class", "temporary_transaction")
# class TestCommons:
#     def test_load_definitions(self):
#         """
#         Test de chargement des schemas
#         """

#         SchemaMethods.init_schemas_definitions()
#         assert 1 == 1

#     def test_load_schemas(self):
#         """
#         Test de chargement des schemas
#         """

#         SchemaMethods.init_schemas_models_and_serializers()
#         assert 1 == 1
