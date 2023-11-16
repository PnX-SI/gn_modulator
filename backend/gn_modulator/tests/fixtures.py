import pytest
import datetime
from geonature.utils.env import db
from m_sipaf.models import PassageFaune, Diagnostic
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from pypnusershub.db.models import Organisme
from geonature.core.gn_synthese.models import TSources, Synthese
from sqlalchemy import func
from apptax.taxonomie.models import Taxref


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


@pytest.fixture()
def synthese_for_passage_faune():
    """
    Seems redondant with synthese_data fixture, but synthese data
    insert in cor_observers_synthese and run a trigger which override the observers_txt field

    """

    with db.session.begin_nested():
        now = datetime.datetime.now()
        taxon = Taxref.query.first()
        point = Point(5.486786, 42.832182)
        geom = from_shape(point, srid=4326)
        source = TSources.query.filter_by(name_source="Occtax").one()
        synthese = Synthese(
            id_source=source.id_source,
            nom_cite=taxon.lb_nom,
            cd_nom=taxon.cd_nom,
            date_min=now,
            date_max=now,
            the_geom_4326=geom,
            the_geom_point=geom,
            the_geom_local=func.st_transform(geom, 2154),
        )
        db.session.add(synthese)
