import pytest  # noqa
from gn_modulator.schema import SchemaMethods


@pytest.mark.usefixtures(scope="session")
class TestSchemas:
    def test_backrefs(self):
        """
        Test sur les backrefs
            - exemple site: modules(backref=sites)
        """
        pass
