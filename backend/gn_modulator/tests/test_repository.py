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
from .fixtures import *


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestRepository:
    from flask import g

    def test_repo_gn_commons_module(self):
        test_schema_repository(
            "commons.module", data_commons.module(), data_commons.module_update()
        )

    def test_repo_gn_meta_ca(self):
        test_schema_repository("meta.ca", data_meta.ca(), data_meta.ca_update())

    def test_repo_gn_meta_jdd(self):
        test_schema_repository("meta.jdd", data_meta.jdd(), data_meta.jdd_update())

    def test_repo_pf_cruved(self, passages_faune_with_diagnostic, users, permission_cache):
        sm = SchemaMethods("m_sipaf.pf")
        uuids_filter_value = ";".join(
            map(lambda x: x.uuid_passage_faune, passages_faune_with_diagnostic)
        )
        params = {
            "filters": [
                f"uuid_passage_faune in {uuids_filter_value}",
            ],
            "fields": ["scope"],
        }
        q = sm.Model().query.query_list(
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["admin_user"].id_role,
        )
        res = q.all()

        assert len(res) == 2

        q = sm.Model().query.query_list(
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["user"].id_role,
        )
        res = q.all()

        assert len(res) == 1

    def test_repo_pf_filter_has_diagnostic(
        self, passages_faune_with_diagnostic, users, permission_cache
    ):
        sm = SchemaMethods("m_sipaf.pf")
        uuids_filter_value = ";".join(
            map(lambda x: x.uuid_passage_faune, passages_faune_with_diagnostic)
        )
        params = {
            "filters": [
                "diagnostics any",
                f"uuid_passage_faune in {uuids_filter_value}",
            ],
            "fields": ["scope"],
        }

        q = sm.Model().query.query_list(
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["admin_user"].id_role,
        )
        res = q.all()

        assert len(res) == 2

    def test_filter_d_within(
        self, passages_faune_with_diagnostic, synthese_for_passage_faune, users, permission_cache
    ):
        sm = SchemaMethods("syn.synthese")
        assert hasattr(sm.Model(), "expression_scope")
        q = sm.Model().query.query_list(
            "SYNTHESE",
            "R",
            {
                "prefilters": [
                    f"the_geom_4326 dwithin m_sipaf.pf;{passages_faune_with_diagnostic[0].id_passage_faune};geom;1000"
                ]
            },
            "select",
            id_role=users["user"].id_role,
        )
        print(q.sql_txt())
        res = q.all()

        assert len(res) == 1
        assert False
