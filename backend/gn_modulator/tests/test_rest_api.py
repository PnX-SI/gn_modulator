"""
    Test pour valider les fonctionalité repository
    - get_one
    - insert
    - update
    - delete
    - list ??
"""

import pytest
from .utils.rest import test_schema_rest
from .data import commons as data_commons


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestRest:
    def test_gn_commons_module(self, client, users):
        test_schema_rest(
            client,
            users["admin_user"],
            "MODULATOR",
            "commons.module",
            data_commons.module(),
            data_commons.module_update(),
        )
