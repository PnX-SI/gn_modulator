"""
    Données exemples pour les test
"""

from gn_modules.schema import SchemaMethods


def get_acquisition_framework_id():
    sm_ca = SchemaMethods("meta.ca")
    ca_data = ca()
    ca_row = sm_ca.get_row_as_dict(
        ca_data["acquisition_framework_name"],
        field_name="acquisition_framework_name",
    )

    if not ca_row:
        sm_ca.insert_row(ca_data)
        ca_row = sm_ca.get_row_as_dict(
            ca_data["acquisition_framework_name"],
            field_name="acquisition_framework_name",
        )
    return ca_row["id_acquisition_framework"]


def ca():
    return {
        "acquisition_framework_name": "test pytest",
        "acquisition_framework_desc": "test pytest",
        "acquisition_framework_start_date": "2018-10-13",
    }


def ca_update():
    return {
        "acquisition_framework_desc": "test pytest 2",
    }


def jdd():
    return {
        "id_acquisition_framework": get_acquisition_framework_id(),
        "dataset_shortname": "truc",
        "dataset_desc": "truc",
        "dataset_name": "muche",
        "marine_domain": True,
        "terrestrial_domain": True,
    }


def jdd_update():
    return {
        "dataset_name": "muche",
    }
