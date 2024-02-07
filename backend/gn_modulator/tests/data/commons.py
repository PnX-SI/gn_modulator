"""
  Données exemple pour les test
"""

from gn_modulator import SchemaMethods


def module():
    return {
        "module_code": "TEST_PYTEST",
        "module_label": "TEST_PYTEST",
        "module_path": "TEST_PYTEST",
        "module_desc": "TEST_PYTEST",
        "active_frontend": False,
        "active_backend": True,
    }


def module_update():
    return {"module_label": "TEST_PYTEST_UPDATE"}


def pf(user):

    sm_nom = SchemaMethods("ref_nom.nomenclature")
    id_nomenclature_type_actor = sm_nom.get_row_as_dict(
        ["PF_TYPE_ACTOR", "CON"],
        ["nomenclature_type.mnemonique", "cd_nomenclature"],
        fields=["id_nomenclature"],
    )["id_nomenclature"]

    return {
        "uuid_passage_faune": "f5e5dd42-dcc1-4cfd-97ec-04699d78cb9b",
        "nom_usuel_passage_faune": "TEST_PF",
        "geom": {"type": "Point", "coordinates": [0, 45]},
        "id_digitiser": user.id_role,
        "actors": [
            {
                "id_organism": user.id_organisme,
                "id_nomenclature_type_actor": id_nomenclature_type_actor,
            }
        ],
    }


def pf_update():
    return {"geom": {"type": "Point", "coordinates": [0, 46]}}
