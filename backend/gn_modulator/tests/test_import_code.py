import pytest  # noqa
from gn_modulator.utils.env import import_test_dir
from .utils.imports import test_import_code
from gn_modulator import ModuleMethods


@pytest.mark.usefixtures("temporary_transaction", scope="session")
class TestImportCode:
    def test_import_code_pfV1(self):
        if not ModuleMethods.module_config("m_sipaf")["registred"]:
            return

        expected = [
            {"res.nb_process": 1, "res.nb_insert": 1},
            {"res.nb_process": 11, "res.nb_insert": 11},
            {"res.nb_process": 11, "res.nb_insert": 11},
        ]

        test_import_code("m_sipaf.pf_V1", import_test_dir / "import_code/", expected)

    def test_import_code_route(self):
        expected = [
            {"res.nb_process": 1},
            {"res.nb_process": 7, "res.nb_insert": 7},
            {"res.nb_process": 9, "res.nb_insert": 9},
        ]

        test_import_code("ref_geo.route", import_test_dir / "import_code/", expected)
