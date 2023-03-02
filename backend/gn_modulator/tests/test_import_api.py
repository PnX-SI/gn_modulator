import pytest  # noqa
from gn_modulator.utils.env import import_test_dir


@pytest.mark.usefixtures("client_class", "temporary_transaction", scope="session")
class TestImportApi:
    pass
