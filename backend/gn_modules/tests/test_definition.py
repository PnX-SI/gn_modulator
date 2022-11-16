"""
Test pour valider
- que les définition contenues dans le module sont valides
- les messages des remontées d'erreurs
"""

import pytest
from gn_modules.definition import DefinitionMethods


@pytest.mark.usefixtures(scope="session")
class TestDefinitions:
    def test_init_gn_module(self):
        """
        On teste si l'initialisation du module s'est bien déroulée
        - s'il n'y a pas d'erreur dans les définitions
        - si on a bien des schemas, modules et layout à minima
        - si le traitement de ces définition n'entraîne par d'erreurs
        """
        from gn_modules.blueprint import errors_init_module

        # pas d'erreurs à l'initialisation de gn_modules
        assert len(errors_init_module) == 0

        # on a bien chargé des schemas, modules, layouts
        assert len(DefinitionMethods.reference_names()) > 0
        assert len(DefinitionMethods.module_codes()) > 0
        assert len(DefinitionMethods.layout_names()) > 0
