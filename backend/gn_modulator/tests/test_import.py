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
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
            "data_type": "csv",
            "csv_delimiter": ",",
        }
        test_data_file(schema_code, data_file_path, expected_infos=expected_infos)

    def test_synthese2(self):
        """
        pour être sur que le premier import n'est pas persistant
        """

        schema_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_1.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(schema_code, data_file_path, expected_infos=expected_infos)

    def test_ref_geo_linear(self):
        """
        test import_route
        """

        schema_code = "ref_geo.linear_type"
        data_file_path = import_test_dir / "route/linear_type.csv"
        expected_infos = {"res.nb_data": 1}
        test_data_file(schema_code, data_file_path, expected_infos=expected_infos)

        schema_code = "ref_geo.linear_group"
        data_file_path = import_test_dir / "route/route.csv"
        pre_process_file_path = import_test_dir / "route/pp_linear_group.sql"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(
            schema_code, data_file_path, pre_process_file_path, expected_infos=expected_infos
        )

        schema_code = "ref_geo.linear"
        data_file_path = import_test_dir / "route/route.csv"
        pre_process_file_path = import_test_dir / "route/pp_linear.sql"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(
            schema_code, data_file_path, pre_process_file_path, expected_infos=expected_infos
        )
