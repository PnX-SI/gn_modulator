"""
    Test pour valider les fonctionalité repository
    - get_one
    - insert
    - update
    - delete
    TODO

    - fields
    - list && cruved??
"""

import pytest

from flask import url_for

from pypnusershub.tests.utils import set_logged_user_cookie, unset_logged_user_cookie

from gn_modulator import ModuleMethods
from .utils.rest import test_schema_rest
from .data import commons as data_commons
from .fixtures import passages_faune_with_diagnostic


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestRest:
    # def test_gn_commons_module(self, client, users):
    #     test_schema_rest(
    #         client,
    #         users["admin_user"],
    #         "MODULATOR",
    #         "commons.module",
    #         data_commons.module(),
    #         data_commons.module_update(),
    #     )

    def test_m_sipaf_pf(self, client, users):
        test_schema_rest(
            client,
            users["admin_user"],
            "m_sipaf",
            "site",
            data_commons.pf(),
            data_commons.pf_update(),
            breadcrumbs_page_code="site_details",
        )

    def test_api_export(self, client, users, passages_faune_with_diagnostic):
        set_logged_user_cookie(client, users["admin_user"])
        r = client.get(
            url_for(
                "modulator.api_export",
                module_code="m_sipaf",
                object_code="site",
                export_code="m_sipaf.pf",
            )
        )
        assert r.status_code == 200
        unset_logged_user_cookie(client)

    def test_valid_fields(self, client, users):
        """
        test fields valide avec espaces au milieu
        """
        set_logged_user_cookie(client, users["admin_user"])
        r = client.get(
            url_for(
                "modulator.api_rest_get_one",
                value="MODULATOR",
                module_code="MODULATOR",
                object_code="commons.module",
                field_name="module_code",
                fields="id_module,module_code, module_label",
            )
        )
        assert r.status_code == 200
        unset_logged_user_cookie(client)

    def test_unvalid_fields(self, client, users):
        """
        test unvalid_fields
        """
        set_logged_user_cookie(client, users["admin_user"])
        r = client.get(
            url_for(
                "modulator.api_rest_get_one",
                value="MODULATOR",
                module_code="MODULATOR",
                object_code="commons.module",
                field_name="module_code",
                fields="id_module,module_code,module_labelo",
            )
        )
        assert r.status_code == 403
        data = r.json
        assert data["code"] == "ERR_REST_API_UNVALID_FIELD"
        assert "module_labelo" in data["unvalid_fields"]
        unset_logged_user_cookie(client)

    def test_unauthorized_fields_read(self, client, users):
        """
        test unvalid_fields
        """
        set_logged_user_cookie(client, users["admin_user"])
        r = client.get(
            url_for(
                "modulator.api_rest_get_one",
                value="MODULATOR",
                module_code="MODULATOR",
                object_code="commons.module",
                field_name="module_code",
                fields="id_module,module_code,datasets",
            )
        )
        assert r.status_code == 403
        data = r.json
        assert data["code"] == "ERR_REST_API_UNAUTHORIZED_FIELD"
        assert "datasets" in data["unauthorized_fields"]
        unset_logged_user_cookie(client)

    def test_unauthorized_fields_write(self, client, users):
        """
        test unvalid_fields
        """
        ModuleMethods.add_actions("MODULATOR", "commons.module", "U")
        autorized_fields = ModuleMethods.get_autorized_fields(
            "MODULATOR", "commons.module", "write"
        )
        autorized_fields.append("module_label")

        set_logged_user_cookie(client, users["admin_user"])
        r = client.patch(
            url_for(
                "modulator.api_rest_get_one",
                value="MODULATOR",
                module_code="MODULATOR",
                object_code="commons.module",
                field_name="module_code",
                fields="id_module,module_code, module_label",
            ),
            data={"module_code": "MALADATA", "module_label": "Plouplou"},
        )
        data = r.json
        assert r.status_code == 200

        # module_code n'a pas été modifié
        assert data["module_code"] == "MODULATOR"

        # module_label est bien modifié
        assert data["module_label"] == "Plouplou"
