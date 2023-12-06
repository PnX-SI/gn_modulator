import pytest
from geonature.utils.env import db
from gn_modulator import SchemaMethods
from gn_modulator.query.repository import query_list


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestRepository:
    def test_schematisable(self):
        sm = SchemaMethods("m_sipaf.pf")

        # model
        Model = sm.Model()
        assert hasattr(Model, "is_schematisable")
        assert Model.is_schematisable
        assert Model.pk_field_names() == ["id_passage_faune"]
        q = query_list(
            Model,
            "m_sipaf",
            "R",
            {"fields": ["id_passage_faune", "nomenclatures_ouvrage_type.label_fr"]},
            "select",
        )
        res = db.session.execute(q).unique()
        sm.serialize_list(res, fields=["nomenclatures_ouvrage_type.label_fr"])
