import pytest  # noqa
from gn_modulator.schema import SchemaMethods


@pytest.mark.usefixtures(scope="session")
class TestSchemas:
    def test_query_sipaf(self):
        """ """
        sm = SchemaMethods("m_sipaf.pf")
        sm.process_features("m_sipaf.pf_test", commit=False)
        params = {
            "fields": [
                "nom_usuel_passage_faune",
                "actors.id_organism",
                "actors.role.nom_role",
                "actors.role.nom_complet",
            ],
            "filters": "nom_usuel_passage_faune = TEST_SIPAF",
        }
        query = sm.query_list("m_sipaf", "R", params)
        sql_txt = sm.format_sql(sm.sql_txt(query))
        print(sql_txt)
        res = query.all()
        print(params["fields"])
        res = sm.serialize_list(res, params["fields"])
        print(res)
        assert "prenom_role" in sql_txt
