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
from gn_modulator import SchemaMethods, ModuleMethods
from gn_modulator import SchemaMethods
from gn_modulator.query.repository import query_list
from gn_modulator.query.utils import pretty_sql
from .fixtures import passages_faune_with_diagnostic
from geonature.tests.fixtures import *
from geonature.tests.test_permissions import g_permissions
from geonature.utils.env import db


@pytest.mark.usefixtures("client_class", "temporary_transaction", "g_permissions")
class TestRepository:
    from flask import g

    def test_pretty_sql(self):
        sm = SchemaMethods('m_sipaf.pf')
        q = query_list(sm.Model(), 'm_sipaf', 'R', {}, 'select')
        pretty_sql(q)

    def test_repo_gn_commons_module(self):
        test_schema_repository(
            "commons.module", data_commons.module(), data_commons.module_update()
        )

    def test_repo_gn_meta_ca(self):
        test_schema_repository("meta.ca", data_meta.ca(), data_meta.ca_update())

    def test_repo_gn_meta_jdd(self):
        test_schema_repository("meta.jdd", data_meta.jdd(), data_meta.jdd_update())

    def test_repo_diag(self, users, passages_faune_with_diagnostic):
        sm = SchemaMethods("m_sipaf.diag")
        fields = ["scope", "id_diagnostic"]
        params = {
            "fields": fields,
        }
        q = query_list(
            sm.Model(),
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["admin_user"].id_role,
        )

        m_list = q.all()
        res = sm.serialize_list(m_list, fields)
        assert True

    def test_repo_pf_rel(self, passages_faune_with_diagnostic, users):
        sm = SchemaMethods("m_sipaf.pf")
        uuids_filter_value = ";".join(
            map(lambda x: x.uuid_passage_faune, passages_faune_with_diagnostic)
        )
        fields = [
            # "code_ouvrage_gestionnaire",
            # "nom_usuel_passage_faune",
            # "uuid_passage_faune",
            # "date_creation_ouvrage",
            # "issu_requalification",
            # "date_requalification_ouvrage",
            # "digitiser.nom_complet",
            "actors.organisme.nom_organisme",
            "linears.additional_data.largeur"
            # "actors.nomenclature_type_actor.label_fr",
            # "label_infrastructures",
            # "linears.additional_data.largeur",
            # "label_communes",
            # "label_departements",
            # "label_regions",
            # "geom_x",
            # "geom_y",
            # "pk",
            # "pr",
            # "pr_abs",
            # "nomenclature_ouvrage_specificite.label_fr",
            # "nomenclatures_ouvrage_materiaux.label_fr",
            # "nomenclatures_ouvrage_type.label_fr",
            # "nomenclatures_ouvrage_type.cd_nomenclature",
            # "ouvrage_type_autre",
            # "pi_ou_ps",
            # "ouvrage_hydrau",
            # "usages.nomenclature_usage_type.label_fr",
            # "usages.detail_usage",
            # "usages.commentaire",
            # "nomenclatures_ouvrage_categorie.label_fr",
            # "largeur_ouvrage",
            # "hauteur_ouvrage",
            # "longueur_franchissement",
            # "largeur_dispo_faune",
            # "hauteur_dispo_faune",
            # "diametre",
            # "nomenclature_ouvrage_hydrau_position.label_fr",
            # "nomenclature_ouvrage_hydrau_banq_caract.label_fr",
            # "nomenclature_ouvrage_hydrau_banq_type.label_fr",
            # "ouvrag_hydrau_tirant_air",
            # "medias",
            # "id_passage_faune",
            # "scope",
        ]
        params = {
            "filters": [
                f"uuid_passage_faune in {uuids_filter_value}",
            ],
            "fields": fields,
        }
        q = query_list(
            sm.Model(),
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["admin_user"].id_role,
        )
        m_list = q.all()
        res = sm.serialize_list(m_list, fields)

        assert len(res) == 2

    def test_repo_pf_nomenclature_spe(self):
        smNom = SchemaMethods("ref_nom.nomenclature")
        authorized_fields_write = ModuleMethods.get_autorized_fields("m_sipaf", "site", "write")
        id_nom_mix = smNom.get_row_as_dict(
            ["PF_OUVRAGE_SPECIFICITE", "MIX"], ["nomenclature_type.mnemonique", "cd_nomenclature"]
        )["id_nomenclature"]
        id_nom_spe = smNom.get_row_as_dict(
            ["PF_OUVRAGE_SPECIFICITE", "SPE"], ["nomenclature_type.mnemonique", "cd_nomenclature"]
        )["id_nomenclature"]
        sm = SchemaMethods("m_sipaf.pf")
        uuid_pf = "1b1edbc2-48ab-4eec-8991-07236b175ca4"
        sm.insert_row(
            {
                "uuid_passage_faune": uuid_pf,
                "geom": {"type": "Point", "coordinates": [45, 0]},
                "nomenclature_ouvrage_specificite": {"id_nomenclature": id_nom_mix},
            },
            authorized_write_fields=authorized_fields_write,
            commit=False,
        )

        res = sm.get_row_as_dict(
            uuid_pf,
            "uuid_passage_faune",
            fields=["nomenclature_ouvrage_specificite.cd_nomenclature"],
        )
        res_nom = res["nomenclature_ouvrage_specificite"]["cd_nomenclature"]
        assert res_nom == "MIX"

        # changer nomenclature_ouvrage_specificite à SPE
        sm.update_row(
            uuid_pf,
            {"nomenclature_ouvrage_specificite": {"id_nomenclature": id_nom_spe}},
            "uuid_passage_faune",
            authorized_write_fields=authorized_fields_write,
            commit=False,
        )
        res = sm.get_row_as_dict(
            uuid_pf,
            "uuid_passage_faune",
            fields=["nomenclature_ouvrage_specificite.cd_nomenclature"],
        )
        res_nom = res["nomenclature_ouvrage_specificite"]["cd_nomenclature"]
        assert res_nom == "SPE"

        # changer nomenclature_ouvrage_specificite à None
        sm.update_row(
            uuid_pf,
            {"nomenclature_ouvrage_specificite": None},
            "uuid_passage_faune",
            authorized_write_fields=authorized_fields_write,
            commit=False,
        )
        res = sm.get_row_as_dict(
            uuid_pf,
            "uuid_passage_faune",
            fields=["nomenclature_ouvrage_specificite.cd_nomenclature"],
        )
        res_nom = res["nomenclature_ouvrage_specificite"]
        assert res_nom is None

    def test_repo_pf_cruved(self, passages_faune_with_diagnostic, users):
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
        q = query_list(
            sm.Model(),
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["admin_user"].id_role,
        )
        m_list = q.all()
        res = sm.serialize_list(m_list, fields)

        assert len(res) == 2

        q = query_list(
            sm.Model(),
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["user"].id_role,
        )
        m_list = q.all()
        res = sm.serialize_list(m_list, fields)

        assert len(res) == 1

    def test_repo_pf_filter_has_diagnostic(self, passages_faune_with_diagnostic, users):
        sm = SchemaMethods("m_sipaf.pf")
        uuids_filter_value = ";".join(
            map(lambda x: x.uuid_passage_faune, passages_faune_with_diagnostic)
        )
        fields = ["scope", "actors.id_organism"]

        params = {
            "filters": [
                "diagnostics any",
                f"uuid_passage_faune in {uuids_filter_value}",
            ],
            "fields": fields,
        }

        q = query_list(
            sm.Model(),
            "m_sipaf",
            "R",
            params,
            "select",
            id_role=users["admin_user"].id_role,
        )
        m_list = q.all()
        res = sm.serialize_list(m_list, fields)
        assert len(res) == 2

    def test_repo_synthese_d_within(
        self, passages_faune_with_diagnostic, synthese_data, users, g_permissions
    ):
        sm = SchemaMethods("syn.synthese")
        q = query_list(
            sm.Model(),
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
        m_list = q.all()
        res = sm.serialize_list(m_list, fields=["id_synthese"])

        assert len(res) == 4

    def test_repo_synthese_scope(self, synthese_data, users, datasets):
        datasets
        sm = SchemaMethods("syn.synthese")
        res = {}
        comment_description_filter_list = ";".join(list(synthese_data.keys()))
        fields = ["scope", "comment_description", "dataset.dataset_name"]
        for user in users:
            q = query_list(
                sm.Model(),
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
        fields = ["scope", "comment_description", "nomenclature_sensitivity.cd_nomenclature"]
        for user in users:
            # continue
            q = query_list(
                sm.Model(),
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
