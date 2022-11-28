import pytest
from gn_modules.module import ModuleMethods
from gn_modules.definition import DefinitionMethods
from gn_modules.utils.env import definitions_test_dir
from gn_modules.utils.errors import get_errors, clear_errors
from gn_modules.utils.cache import set_global_cache, get_global_cache
from gn_modules.schema import SchemaMethods
from .utils import load_module_from_file
from gn_modules import init_gn_modules


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestModules:
    def test_install_remove_module(self):
        """
        tester un cycle d'installation / désinstallation d'un module
        TODO initialisation + sql / alembic
        """

        clear_errors()

        module_code = "pytest_1"

        # test si le module n'est pas en base avant de commencer le test
        res = SchemaMethods("commons.module").get_row_as_dict(
            module_code, field_name="module_code", fields=["module_code"]
        )
        assert res is None

        module_config = load_module_from_file(
            definitions_test_dir / "modules/test1/pytest_1.module.yml"
        )

        assert len(get_errors()) == 0

        assert module_config is not None
        assert module_config["code"] == module_code
        assert module_config["registred"] is False

        # install module
        module_installed = ModuleMethods.install_module(module_code)
        assert module_installed is True

        # test si le module est bien en base
        res = SchemaMethods("commons.module").get_row_as_dict(
            module_code, field_name="module_code", fields=["module_code"]
        )
        assert res is not None
        assert res["module_code"] == module_code

        # suppression du module
        module_removed = ModuleMethods.remove_module(module_code)
        assert module_removed is True

        # test si le module n'est plus en base
        res = SchemaMethods("commons.module").get_row_as_dict(
            module_code, field_name="module_code"
        )
        assert res is None

        set_global_cache(["module", module_code], None)

        assert get_global_cache(["module", module_code]) is None

    def test_install_remove_module_with_dependancies(self):
        """
        tester un cycle d'installation / désinstallation d'un module avec dépendances
        """

        clear_errors()

        for module_code_ in ["pytest_1", "pytest_2"]:
            res = SchemaMethods("commons.module").get_row_as_dict(
                module_code_, field_name="module_code", fields=["module_code"]
            )
            assert res is None

        module_config_1 = load_module_from_file(
            definitions_test_dir / "modules/test1/pytest_1.module.yml"
        )
        assert len(get_errors()) == 0
        assert module_config_1 is not None
        assert module_config_1["code"] == "pytest_1"
        assert module_config_1["registred"] is False

        module_config_2 = load_module_from_file(
            definitions_test_dir / "modules/test2/pytest_2.module.yml"
        )
        assert len(get_errors()) == 0
        assert module_config_2 is not None
        assert module_config_2["code"] == "pytest_2"
        assert module_config_2["registred"] is False
        assert module_config_2["dependencies"] == ["pytest_1"]

        # install module
        module_installed = ModuleMethods.install_module("pytest_2")
        assert module_installed is False

        module_installed = ModuleMethods.install_module("pytest_2", force=True)
        assert module_installed is True

        # test si les modules sont bien en base
        for module_code in ["pytest_1", "pytest_2"]:
            res = SchemaMethods("commons.module").get_row_as_dict(
                module_code, field_name="module_code", fields=["module_code"]
            )
            assert res is not None
            assert res["module_code"] == module_code

        # suppression du module
        module_removed = ModuleMethods.remove_module("pytest_1")
        assert module_removed is False

        # test si les modules sont bien en base
        for module_code in ["pytest_1", "pytest_2"]:
            res = SchemaMethods("commons.module").get_row_as_dict(
                module_code, field_name="module_code", fields=["module_code"]
            )
            assert res is not None
            assert res["module_code"] == module_code

        # suppression du module
        module_removed = ModuleMethods.remove_module("pytest_1", force=True)
        assert module_removed is True

        # test si les modules sont bien en base
        for module_code in ["pytest_1", "pytest_2"]:
            res = SchemaMethods("commons.module").get_row_as_dict(
                module_code, field_name="module_code", fields=["module_code"]
            )
            assert res is None
