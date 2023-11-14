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
from .fixtures import passage_faune_with_diagnostic


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestRepository:
    def test_gn_commons_module(self):
        test_schema_repository(
            "commons.module", data_commons.module(), data_commons.module_update()
        )

    def test_gn_meta_ca(self):
        test_schema_repository("meta.ca", data_meta.ca(), data_meta.ca_update())

    def test_gn_meta_jdd(self):
        test_schema_repository("meta.jdd", data_meta.jdd(), data_meta.jdd_update())

    def test_filter_has_diagnostic(self, passage_faune_with_diagnostic):
        sm = SchemaMethods("m_sipaf.pf")
        q = sm.query_list(
            "m_sipaf.pf",
            "R",
            {
                "filters": [
                    "diagnostics any",
                    f"uuid_passage_faune = {passage_faune_with_diagnostic.uuid_passage_faune}",
                ]
            },
        )
        res = q.all()

        assert len(res) == 1
