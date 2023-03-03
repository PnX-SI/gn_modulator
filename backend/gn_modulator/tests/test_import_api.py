import pytest  # noqa
from flask import url_for
from werkzeug.datastructures import Headers

from geonature.tests.utils import set_logged_user_cookie

from gn_modulator.utils.env import import_test_dir


@pytest.mark.usefixtures("client_class", "temporary_transaction", scope="session")
class TestImportApi:
    def test_import_synthese(self, users):
        set_logged_user_cookie(self.client, users["admin_user"])
        with open(import_test_dir / "synthese_1.csv", "rb") as f:
            data = {"file": (f, "synthese.csv"), "object_code": "syn.synthese"}
            r = self.client.post(
                url_for("modulator.api_import", module_code="MODULATOR"),
                data=data,
                headers=Headers({"Content-Type": "multipart/form-data"}),
            )
            print(r.data)
            assert r.status_code == 200, r.data
