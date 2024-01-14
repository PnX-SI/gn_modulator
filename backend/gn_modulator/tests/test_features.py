"""
    Test pour valider les fonctionalité repository
    - get_one
    - insert
    - update
    - delete
    - list ??
"""

import pytest
from gn_modulator import SchemaMethods


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestRepository:
    def test_feature(self):
        SchemaMethods.process_features("m_sipaf.utils")
        assert True
