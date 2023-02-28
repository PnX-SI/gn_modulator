import pytest  # noqa
from gn_modulator.utils.env import import_test_dir
from .utils.imports import test_data_file


@pytest.mark.usefixtures("temporary_transaction", scope="session")
class TestImport:
    def test_synthese(self):
        """
        premier test ajout d'une ligne dans la synthese
        """

        schema_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_1.csv"
        expected_infos = {
            "nb_data": 2,
            "nb_insert": 2,
            "nb_update": 0,
            "nb_unchanged": 0,
        }
        test_data_file(schema_code, data_file_path, expected_infos=expected_infos)

    def test_route(self):
        """
        test import_route
        """

        schema_code = "ref_geo.linear_group"
        data_file_path = import_test_dir / "route/route.csv"
        pre_process_file_path = import_test_dir / "route/pp_linear_group.sql"
        expected_infos = {
            "nb_data": 1,
            "nb_insert": 1,
            "nb_update": 0,
            "nb_unchanged": 0,
        }
        test_data_file(
            schema_code, data_file_path, pre_process_file_path, expected_infos=expected_infos
        )

        schema_code = "ref_geo.linear"
        data_file_path = import_test_dir / "route/route.csv"
        pre_process_file_path = import_test_dir / "route/pp_linear.sql"
        expected_infos = {
            "nb_data": 1,
            "nb_insert": 1,
            "nb_update": 0,
            "nb_unchanged": 0,
        }
        test_data_file(
            schema_code, data_file_path, pre_process_file_path, expected_infos=expected_infos
        )
