"""
    Données exemples pour les test
"""

from gn_modules.schema import SchemaMethods


def get_acquisition_framework_id():
    sm_ca = SchemaMethods("meta.ca")
    res = sm_ca.query_list(params={"limit": 1})
    res = sm_ca.serialize_list(res, ["id_acquisition_framework"])
    return res[0]["id_acquisition_framework"]


def jdd():
    return {
        "id_acquisition_framework": get_acquisition_framework_id(),
        "dataset_shortname": "truc",
        "dataset_desc": "truc",
        "dataset_name": "muche",
        "marine_domain": True,
        "terrestrial_domain": True,
        "meta_create_date": "2018-11-13T20:20:39+00:00",
    }


def jdd_update():
    return {
        "dataset_name": "muche",
    }
