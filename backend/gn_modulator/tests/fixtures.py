import pytest
from geonature.utils.env import db
from m_sipaf.models import PassageFaune, Diagnostic
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from pypnusershub.db.models import Organisme


@pytest.fixture
def passage_faune_with_diagnostic():
    point = Point(5.486786, 42.832182)
    geom = from_shape(point, srid=4326)
    uuid = "0c92af92-000b-401c-9994-f2c12470493a"
    with db.session.begin_nested():
        pf = PassageFaune(geom=geom, uuid_passage_faune=uuid)
        db.session.add(pf)
        organisme = Organisme.query.filter_by(nom_organisme="ALL").one()
        diagnostic = Diagnostic(
            id_organisme=organisme.id_organisme, date_diagnostic="2017-01-08 20:00:00.000"
        )
        pf.diagnostics.append(diagnostic)
    return pf
