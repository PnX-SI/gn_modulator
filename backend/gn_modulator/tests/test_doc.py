"""
    Test pour valider les fonctionalité repository
    - get_one
    - insert
    - update
    - delete
    - list ??
"""

import pytest
from gn_modulator import SchemaMethods


@pytest.mark.usefixtures("client_class")
class TestDoc:
    def test_doc_import_pf(self):
        txt = SchemaMethods("m_sipaf.pf").doc_markdown("import")
        print(txt)
        assert (
            "label_acteur" not in txt
        ), "label_acteur est une column property, elle ne doit pas être dans la doc de l'import"
