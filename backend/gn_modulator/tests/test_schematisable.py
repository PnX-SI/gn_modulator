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
from .data import meta as data_meta
from gn_modulator import SchemaMethods
from .fixtures import passages_faune_with_diagnostic
from geonature.tests.fixtures import *
from geonature.tests.test_permissions import g_permissions


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestSchematizable:
    def test_schematizable_property(self):
        sm = SchemaMethods("m_sipaf.pf")
        Model = sm.Model()

        assert Model.has_property("actors.organisme")
        assert Model.is_relationship("actors.organisme")
        assert Model.has_property("linears.additional_data.youplaboum")
        assert (
            Model.cut_key_to_json("linears.additional_data.youplaboum")
            == "linears.additional_data"
        )
