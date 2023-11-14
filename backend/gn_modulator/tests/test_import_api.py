import pytest  # noqa
from flask import url_for
from werkzeug.datastructures import Headers
from sqlalchemy import and_

from geonature.tests.utils import set_logged_user_cookie, unset_logged_user_cookie
from gn_modulator import ModuleMethods
from gn_modulator.utils.env import import_test_dir
from gn_modulator.imports.models import TImport
from geonature.core.gn_synthese.models import Synthese, TSources
from geonature.utils.env import db


# @pytest.mark.usefixtures("client_class")
# class TestImportApi:
#     def test_api_import_synthese_async(self, users):
#         source = TSources.query.filter_by(name_source="Occtax").one()
#         req_synthese = db.session.query(Synthese).filter(
#             and_(
#                 Synthese.id_source == source.id_source,
#                 Synthese.entity_source_pk_value.in_(["21_", "22_"]),
#             )
#         )

#         req_synthese.delete(synchronize_session=False)
#         db.session.flush()

#         ModuleMethods.add_actions("MODULATOR", "syn.synthese", "I")

#         set_logged_user_cookie(self.client, users["admin_user"])
#         with open(import_test_dir / "synthese_1.csv", "rb") as f:
#             data = {"data_file": (f, "synthese.csv")}
#             r = self.client.post(
#                 url_for(
#                     "modulator.api_import_async",
#                     module_code="MODULATOR",
#                     object_code="syn.synthese",
#                 ),
#                 data=data,
#                 headers=Headers({"Content-Type": "multipart/form-data"}),
#             )

#             assert r.status_code == 200, r.data

#             assert len(r.json["errors"]) == 0, r.json["errors"]
#             print("After post", r.json["status"])

#             id_import = r.json["id_import"]

#             index = 0
#             while r.json["status"] != "DONE":
#                 index += 1
#                 import time

#                 time.sleep(2)
#                 if index > 10:
#                     break
#                 r = self.client.patch(
#                     url_for(
#                         "modulator.api_import_async",
#                         module_code="MODULATOR",
#                         object_code="syn.synthese",
#                         id_import=id_import,
#                     ),
#                     data={},
#                 )
#                 print("After patch", r.json["status"])

#             assert r.json["res"]["nb_data"] == 2
#             assert r.json["res"]["nb_insert"] == 2
#             assert r.json["id_digitiser"] == users["admin_user"].id_role

#             unset_logged_user_cookie(self.client)

#             req_import = TImport.query.filter(TImport.id_import == id_import)
#             impt = req_import.one()

#             assert impt.status == "DONE"

#             req_import.delete()

#             # req_synthese.delete(synchronize_session=False)
#             db.session.flush()

#             assert True

# def test_import_synthese2(self, users):
#     ModuleMethods.add_actions("MODULATOR", "syn.synthese", "I")

#     set_logged_user_cookie(self.client, users["admin_user"])
#     with open(import_test_dir / "synthese_1.csv", "rb") as f:
#         data = {"data_file": (f, "synthese.csv")}
#         r = self.client.post(
#             url_for(
#                 "modulator.api_import", module_code="MODULATOR", object_code="syn.synthese"
#             ),
#             data=data,
#             headers=Headers({"Content-Type": "multipart/form-data"}),
#         )

#         assert r.status_code == 200, r.data

#         assert len(r.json["errors"]) == 0, r.json["errors"]

#         assert r.json["res"]["nb_data"] == 2
#         assert r.json["res"]["nb_insert"] == 2

#         unset_logged_user_cookie(self.client)
