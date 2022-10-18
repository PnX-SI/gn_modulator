"""
    Test pour la nomenclature    -
"""
import os
from pathlib import Path

from gn_modules.schema import SchemaMethods
import pytest
from . import app, temporary_transaction  # noqa


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestModulesData:
    def test_load_and_validate_data(self):
        """
        test si la procédure de chargement et validation
        des fichier json pour les données complémentaires (nomenclature, etc...)
        se passe bien pour tous les fichiers de <gn_module>/config/data
        """

        # test de tous les dossier <data_type> et de tous les fichiers >data_name>.yml
        for root, dirs, files in os.walk(
            SchemaMethods.config_directory() / "data", followlinks=True
        ):

            for f in filter(lambda f: f.endswith(".json"), files):
                data = SchemaMethods.load_and_validate_data(Path(root) / f)
                assert data is not None

    def test_process_nomenclature(self, app):
        """ """
        out = SchemaMethods.process_data_name(None)
        assert out is not None
        return
