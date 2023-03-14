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
        mapping_file_path = import_test_dir / "route/pp_linear_group.sql"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(
            schema_code, data_file_path, mapping_file_path, expected_infos=expected_infos
        )

        schema_code = "ref_geo.linear"
        data_file_path = import_test_dir / "route/route.csv"
        mapping_file_path = import_test_dir / "route/pp_linear.sql"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(
            schema_code, data_file_path, mapping_file_path, expected_infos=expected_infos
        )

    def test_ref_geo_area(self):
        schema_code = "ref_geo.area"
        data_file_path = import_test_dir / "ref_geo.area.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        impt = test_data_file(schema_code, data_file_path, expected_infos=expected_infos)

    #        print(impt.sql["process_view"])
    # assert 1 == 0

    # Test remontées d'erreurs

    def test_error_ERR_IMPORT_INVALID_VALUE_FOR_TYPE(self):
        schema_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_ERR_IMPORT_INVALID_VALUE_FOR_TYPE.csv"
        expected_infos = {"errors": [{"code": "ERR_IMPORT_INVALID_VALUE_FOR_TYPE"}]}
        test_data_file(
            schema_code, data_file_path, mapping_file_path=None, expected_infos=expected_infos
        )

    def test_error_ERR_IMPORT_MISSING_UNIQUE(self):
        schema_code = "ref_geo.area"
        data_file_path = import_test_dir / "ref_geo.area_ERR_IMPORT_MISSING_UNIQUE.csv"
        expected_infos = {"errors": [{"code": "ERR_IMPORT_MISSING_UNIQUE"}]}
        test_data_file(
            schema_code, data_file_path, mapping_file_path=None, expected_infos=expected_infos
        )
