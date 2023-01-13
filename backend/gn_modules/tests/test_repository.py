"""
    Test pour valider les fonctionalité repository
    - get_one
    - insert
    - update
    - delete
    - list ??
"""

import pytest
from .utils.repository import test_schema_repository
from .data import commons as data_commons


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestRepository:
    def test_gn_commons_module(self):
        test_schema_repository("commons.module", data_commons.module)
