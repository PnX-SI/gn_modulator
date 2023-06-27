"""
  Données exemple pour les test
"""


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
    return {
        "module_label": "TEST_PYTEST_UPDATE",
    }


def pf():
    return {
        "code_passage_faune": "TEST_PF",
        "geom": {"type": "Point", "coordinates": [0, 45]},
    }


def pf_update():
    return {
        "geom": {"type": "Point", "coordinates": [0, 46]},
    }
