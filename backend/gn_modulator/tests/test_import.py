import pytest  # noqa
from gn_modulator.utils.env import import_test_dir
from .utils.imports import test_import_data_file
from gn_modulator import SchemaMethods, ModuleMethods
from .fixtures import mappings_field, monitoring


@pytest.mark.usefixtures("temporary_transaction", scope="session")
class TestImport:
    def test_synthese1(self):
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
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

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
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_ref_geo_linear(self, mappings_field):
        """
        test import_route
        """

        module_code = "MODULATOR"
        object_code = "ref_geo.linear_type"
        data_file_path = import_test_dir / "route/linear_type.csv"
        expected_infos = {"res.nb_data": 2}
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

        module_code = "MODULATOR"
        object_code = "ref_geo.linear_group"
        data_file_path = import_test_dir / "route/route.csv"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            id_mapping_field=mappings_field["ref_geo.linear_group__test1"].id_mapping_field,
            expected_infos=expected_infos,
        )

        module_code = "MODULATOR"
        object_code = "ref_geo.linear"
        data_file_path = import_test_dir / "route/route.csv"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
        }
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            id_mapping_field=mappings_field["ref_geo.linear__test1"].id_mapping_field,
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
        impt = test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

        impt.log_sql(import_test_dir / "ref_geo.area.csv.log.sql", "xxx")

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

        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    @pytest.mark.skip()
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
        impt = test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

        impt.log_sql(import_test_dir / "synthese_obs.log.sql", "xxx")

        data_file_path = import_test_dir / "synthese_obs_update.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_insert": 0,
            "res.nb_update": 1,
            "res.nb_unchanged": 1,
            "data_type": "csv",
            "csv_delimiter": ",",
        }
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_synthese_srid(self):
        module_code = "MODULATOR"
        object_code = "syn.synthese"
        options = {"srid": 2154}
        data_file_path = import_test_dir / "synthese_srid.csv"
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
            "data_type": "csv",
            "csv_delimiter": ",",
        }
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
            options=options,
        )

        sm = SchemaMethods(object_code)
        res = sm.get_row_as_dict(
            "test_213", "entity_source_pk_value", fields=["id_synthese", "the_geom_4326"]
        )
        assert res["the_geom_4326"] is not None

    def test_sipaf_xy(self):
        # on s'assure que le module est bien installé
        if not ModuleMethods.module_config("m_sipaf")["registred"]:
            return

        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_xy.csv"
        options = {}
        expected_infos = {
            "res.nb_data": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
            "res.nb_unchanged": 0,
            "data_type": "csv",
            "csv_delimiter": ";",
        }
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
            options=options,
        )

        sm = SchemaMethods("m_sipaf.pf")
        res = sm.get_row_as_dict(
            "TEST_XY", "nom_usuel_passage_faune", fields=["id_passage_faune", "geom"]
        )
        assert res["geom"] is not None

    def test_sipaf_exemple_simple(self):
        if not ModuleMethods.module_config("m_sipaf")["registred"]:
            return

        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_simple.csv"
        expected_infos = {"res.nb_data": 1, "res.nb_insert": 1}
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_sipaf_exemple_simple_uuid(self):
        if not ModuleMethods.module_config("m_sipaf")["registred"]:
            return

        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_simple_uuid.csv"
        expected_infos = {"res.nb_data": 1, "res.nb_insert": 1}
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_import_sipaf_error_missing_uuid(self):
        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_missing_uuid.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_raw": 2,
            "res.nb_process": 2,
            "res.nb_insert": 2,
            "res.nb_update": 0,
        }
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_import_sipaf_exemple_complet(self):
        if not ModuleMethods.module_config("m_sipaf")["registred"]:
            return

        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_complet.csv"
        expected_infos = {"res.nb_data": 1, "res.nb_insert": 1}
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_import_sipaf_update(self):
        if not ModuleMethods.module_config("m_sipaf")["registred"]:
            return

        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_update_1.csv"
        expected_infos = {"res.nb_data": 1, "res.nb_insert": 1, "res.nb_update": 0}
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

        data_file_path = import_test_dir / "pf_update_2.csv"
        expected_infos = {"res.nb_data": 1, "res.nb_insert": 0, "res.nb_update": 1}
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_import_sipaf_actors(self):
        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_actors.csv"
        expected_infos = {
            "res.nb_data": 2,
            "res.nb_raw": 2,
            "res.nb_process": 1,
            "res.nb_insert": 1,
            "res.nb_update": 0,
        }
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    @pytest.mark.skip()
    def test_monitoring(self, monitoring):
        schema_code = "monitoring.site"
        data_file_path = import_test_dir / "monitoring_site_and_visit.csv"
        expected_infos = {"res.nb_data": 3, "res.nb_process": 2, "res.nb_insert": 2}
        test_import_data_file(
            data_file_path,
            schema_code=schema_code,
            expected_infos=expected_infos,
        )

    # Test remontées d'erreurs

    def test_import_error_ERR_IMPORT_INVALID_VALUE_FOR_TYPE(self):
        module_code = "MODULATOR"
        object_code = "syn.synthese"
        data_file_path = import_test_dir / "synthese_ERR_IMPORT_INVALID_VALUE_FOR_TYPE.csv"
        expected_infos = {"errors": [{"error_code": "ERR_IMPORT_INVALID_VALUE_FOR_TYPE"}]}
        test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )

    def test_import_error_ERR_IMPORT_UNRESOLVED(self):
        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_ERR_IMPORT_UNRESOLVED.csv"
        expected_infos = {"errors": [{"error_code": "ERR_IMPORT_UNRESOLVED"}]}
        impt = test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )
        print(impt.pretty_errors_txt())

        assert (
            ", ".join(map(lambda x: x["value"], impt.errors[0]["error_infos"]))
            == "concessionnaire, proprietaire"
        )

    def test_import_error_ERR_IMPORT_REQUIRED(self):
        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_ERR_IMPORT_REQUIRED.csv"
        expected_infos = {"errors": [{"error_code": "ERR_IMPORT_REQUIRED"}]}
        impt = test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )
        print(impt.pretty_errors_txt())

    def test_import_error_ERR_IMPORT_INVALID_VALUE_FOR_TYPE(self):
        module_code = "m_sipaf"
        object_code = "site"
        data_file_path = import_test_dir / "pf_ERR_IMPORT_INVALID_VALUE_FOR_TYPE.csv"
        expected_infos = {"errors": [{"error_code": "ERR_IMPORT_INVALID_VALUE_FOR_TYPE"}]}
        impt = test_import_data_file(
            data_file_path,
            module_code=module_code,
            object_code=object_code,
            expected_infos=expected_infos,
        )
        print(impt.pretty_errors_txt())
