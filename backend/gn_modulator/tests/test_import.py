import pytest  # noqa
from gn_modulator.utils.env import import_test_dir
from .utils.imports import test_data_file


@pytest.mark.usefixtures("temporary_transaction", scope="session")
class TestImport:
    def test_synthese(self):
        """
        premier test ajout d'une ligne dans la synthese
        """

        module_code = "MODULATOR"
        object_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_1.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
            "data_type": "csv",
            "csv_delimiter": ",",
        }
        test_data_file(module_code, object_code, data_file_path, expected_infos=expected_infos)

    def test_synthese2(self):
        """
        pour être sur que le premier import n'est pas persistant
        """

        module_code = "MODULATOR"
        object_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_1.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(module_code, object_code, data_file_path, expected_infos=expected_infos)

    def test_ref_geo_linear(self):
        """
        test import_route
        """

        module_code = "MODULATOR"
        object_code = "ref_geo.linear_type"
        data_file_path = import_test_dir / "route/linear_type.csv"
        expected_infos = {"res.nb_data": 1}
        test_data_file(module_code, object_code, data_file_path, expected_infos=expected_infos)

        module_code = "MODULATOR"
        object_code = "ref_geo.linear_group"
        data_file_path = import_test_dir / "route/route.csv"
        mapping_file_path = import_test_dir / "route/pp_linear_group.sql"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(
            module_code,
            object_code,
            data_file_path,
            mapping_file_path,
            expected_infos=expected_infos,
        )

        module_code = "MODULATOR"
        object_code = "ref_geo.linear"
        data_file_path = import_test_dir / "route/route.csv"
        mapping_file_path = import_test_dir / "route/pp_linear.sql"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_data_file(
            module_code,
            object_code,
            data_file_path,
            mapping_file_path,
            expected_infos=expected_infos,
        )

    def test_ref_geo_area(self):
        module_code = "MODULATOR"
        object_code = "ref_geo.area"
        data_file_path = import_test_dir / "ref_geo.area.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        impt = test_data_file(
            module_code, object_code, data_file_path, expected_infos=expected_infos
        )

        print(impt.sql["insert"])
        print(impt.sql["update"])
        print(impt.sql["nb_insert"])
        print(impt.sql["nb_update"])

    def test_synthese_x_y(self):
        module_code = "MODULATOR"
        object_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_xy.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
            "data_type": "csv",
            "csv_delimiter": ",",
        }
        test_data_file(module_code, object_code, data_file_path, expected_infos=expected_infos)

    def test_synthese_update_obs(self):
        module_code = "MODULATOR"
        object_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_obs.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
            "data_type": "csv",
            "csv_delimiter": ",",
        }
        test_data_file(module_code, object_code, data_file_path, expected_infos=expected_infos)

        data_file_path = import_test_dir / "synthese_obs_update.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 0,
            "res.nb_update": 1,
            "res.nb_unchanged": 1,
            "data_type": "csv",
            "csv_delimiter": ",",
        }
        test_data_file(module_code, object_code, data_file_path, expected_infos=expected_infos)

    # Test remontées d'erreurs

    def test_error_ERR_IMPORT_INVALID_VALUE_FOR_TYPE(self):
        module_code = "MODULATOR"
        object_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_ERR_IMPORT_INVALID_VALUE_FOR_TYPE.csv"
        expected_infos = {"errors": [{"code": "ERR_IMPORT_INVALID_VALUE_FOR_TYPE"}]}
        test_data_file(
            module_code,
            object_code,
            data_file_path,
            mapping_file_path=None,
            expected_infos=expected_infos,
        )

    def test_error_ERR_IMPORT_MISSING_UNIQUE(self):
        module_code = "MODULATOR"
        object_code = "ref_geo.area"
        data_file_path = import_test_dir / "ref_geo.area_ERR_IMPORT_MISSING_UNIQUE.csv"
        expected_infos = {"errors": [{"code": "ERR_IMPORT_MISSING_UNIQUE"}]}
        test_data_file(
            module_code,
            object_code,
            data_file_path,
            mapping_file_path=None,
            expected_infos=expected_infos,
        )
