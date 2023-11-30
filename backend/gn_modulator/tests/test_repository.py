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

    def test_repo_pf_cruved(self, passages_faune_with_diagnostic, users, g_permissions):
        sm = SchemaMethods("m_sipaf.pf")
        uuids_filter_value = ";".join(
            map(lambda x: x.uuid_passage_faune, passages_faune_with_diagnostic)
        )
        fields = ["scope", "uuid_passage_faune"]
        params = {
            "filters": [
                f"uuid_passage_faune in {uuids_filter_value}",
            ],
            "fields": fields,
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
        m_list = q.all()
        res = sm.serialize_list(m_list, fields)

        assert len(res) == 1

    def test_repo_pf_filter_has_diagnostic(
        self, passages_faune_with_diagnostic, users, g_permissions
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
            "fields": ["scope", "actors"],
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

    def test_repo_synthese_d_within(
        self, passages_faune_with_diagnostic, synthese_data, users, g_permissions
    ):
        sm = SchemaMethods("syn.synthese")
        q = sm.Model().query.query_list(
            "SYNTHESE",
            "R",
            {
                "prefilters": [
                    f"the_geom_4326 dwithin m_sipaf.pf;{passages_faune_with_diagnostic[0].id_passage_faune};geom;1000"
                ]
            },
            "select",
            id_role=users["admin_user"].id_role,
        )
        res = q.all()

        assert len(res) == 4

    def test_repo_synthese_scope(self, synthese_data, users, g_permissions, datasets):
        datasets
        sm = SchemaMethods("syn.synthese")
        res = {}
        comment_description_filter_list = ";".join(list(synthese_data.keys()))
        fields = ["scope", "comment_description", "dataset.dataset_name"]
        for user in users:
            q = sm.Model().query.query_list(
                "SYNTHESE",
                "R",
                {
                    "fields": fields,
                    "filters": f"comment_description in {comment_description_filter_list}",
                },
                "select",
                id_role=users[user].id_role,
            )

            m_list = q.all()
            res[user] = sm.serialize_list(m_list, fields=fields)

            if user in ["admin_user", "user", "self_user"]:
                assert len(res[user]) == 9
                assert all(r["scope"] == 1 for r in res[user])

            if user in ["associate_user"]:
                assert len(res[user]) == 9
                assert all(r["scope"] == 2 for r in res[user])

    def test_repo_synthese_permission(self, synthese_sensitive_data, users, g_permissions):
        for key in synthese_sensitive_data:
            s = synthese_sensitive_data[key]
        sm = SchemaMethods("syn.synthese")
        res = {}
        comment_description_filter_list = ";".join(list(synthese_sensitive_data.keys()))
        fields = [
            "scope",
            "comment_description",
            "nomenclature_sensitivity.cd_nomenclature",
        ]
        for user in users:
            # continue
            q = sm.Model().query.query_list(
                "SYNTHESE",
                "R",
                {
                    "fields": fields,
                    "filters": f"comment_description in {comment_description_filter_list}",
                },
                "select",
                id_role=users[user].id_role,
            )
            m_list = q.all()
            res[user] = sm.serialize_list(m_list, fields=fields)

        for user in users:
            if user in ["self_user"]:
                assert len(res[user]) == 3
                assert all(r["scope"] == 1 for r in res[user])

            if user in ["admin_user", "user", "associate_user"]:
                assert len(res[user]) == 3
                assert all(r["scope"] == 2 for r in res[user])

            if user in ["associate_user_2_exclude_sensitive"]:
                assert len(res[user]) == 1
                assert all(r["scope"] == 2 for r in res[user])
