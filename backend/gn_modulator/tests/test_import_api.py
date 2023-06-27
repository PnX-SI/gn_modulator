import pytest  # noqa
from flask import url_for
from werkzeug.datastructures import Headers

from geonature.tests.utils import set_logged_user_cookie, unset_logged_user_cookie
from gn_modulator import ModuleMethods
from gn_modulator.utils.env import import_test_dir


@pytest.mark.usefixtures("client_class", "temporary_transaction", scope="session")
class TestImportApi:
    def test_import_synthese(self, users):
        ModuleMethods.add_actions("MODULATOR", "syn.synthese", "I")

        set_logged_user_cookie(self.client, users["admin_user"])
        with open(import_test_dir / "synthese_1.csv", "rb") as f:
            data = {"data_file": (f, "synthese.csv")}
            r = self.client.post(
                url_for(
                    "modulator.api_import", module_code="MODULATOR", object_code="syn.synthese"
                ),
                data=data,
                headers=Headers({"Content-Type": "multipart/form-data"}),
            )

            assert r.status_code == 200, r.data

            assert len(r.json["errors"]) == 0, r.json["errors"]

            assert r.json["res"]["nb_data"] == 2
            assert r.json["res"]["nb_insert"] == 2

            assert r.json["id_digitiser"] == users["admin_user"].id_role

            unset_logged_user_cookie(self.client)

    def test_import_synthese2(self, users):
        ModuleMethods.add_actions("MODULATOR", "syn.synthese", "I")

        set_logged_user_cookie(self.client, users["admin_user"])
        with open(import_test_dir / "synthese_1.csv", "rb") as f:
            data = {"data_file": (f, "synthese.csv")}
            r = self.client.post(
                url_for(
                    "modulator.api_import", module_code="MODULATOR", object_code="syn.synthese"
                ),
                data=data,
                headers=Headers({"Content-Type": "multipart/form-data"}),
            )

            assert r.status_code == 200, r.data

            assert len(r.json["errors"]) == 0, r.json["errors"]

            assert r.json["res"]["nb_data"] == 2
            assert r.json["res"]["nb_insert"] == 2

            unset_logged_user_cookie(self.client)
