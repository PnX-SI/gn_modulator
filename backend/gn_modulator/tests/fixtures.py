import pytest
import datetime
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
import sqlalchemy as sa

from geonature.utils.env import db
from pypnnomenclature.repository import get_nomenclature_id_term
from pypnusershub.db.models import Organisme
from geonature.core.gn_commons.models import TModules
from geonature.core.gn_meta.models import TDatasets, TAcquisitionFramework
from m_sipaf.models import PassageFaune, Diagnostic, Actor
from gn_modulator.imports.models import TMappingField, TMappingValue


@pytest.fixture
def passages_faune_with_diagnostic(users):
    point = Point(5.92, 45.56)
    geom = from_shape(point, srid=4326)
    uuids = ["0c92af92-000b-401c-9994-f2c12470493a", "0c92af92-000b-401c-9994-f2c12470493b"]
    passages_faune = []

    organisme = db.session.execute(
        sa.select(Organisme).filter_by(nom_organisme="ALL")
    ).scalar_one()

    with db.session.begin_nested():
        for uuid in uuids:
            pf = PassageFaune(geom=geom, uuid_passage_faune=uuid)
            db.session.add(pf)

            pf.diagnostics.append(
                Diagnostic(
                    id_organisme=organisme.id_organisme, date_diagnostic="2017-01-08 20:00:00.000"
                )
            )
            if uuid == "0c92af92-000b-401c-9994-f2c12470493a":
                pf.actors.append(
                    Actor(
                        id_organism=users["user"].id_organisme,
                        id_nomenclature_type_actor=sa.func.ref_nomenclatures.get_id_nomenclature(
                            "PF_TYPE_ACTOR", "PRO"
                        ),
                    )
                )
            passages_faune.append(pf)
    return passages_faune


@pytest.fixture
def monitoring():
    monitoring_fixture = {}
    with db.session.begin_nested():
        module = TModules(
            module_code="monitornig_test",
            module_label="monitoring module",
            active_frontend=True,
            active_backend=True,
            module_path="monitoring_test",
        )
        db.session.add(module)

        af = TAcquisitionFramework(
            acquisition_framework_name="monitornig_test",
            acquisition_framework_desc="monitornig_test",
            unique_acquisition_framework_id="3767fcd3-e152-49f5-aaa3-8710e4d8152b",
        )

        db.session.add(af)

        jdd = TDatasets(
            dataset_name="monitoring_test",
            unique_dataset_id="8199b7d4-a888-4dbc-9979-9fb308318587",
            dataset_shortname="monitoring_test",
            dataset_desc="monitoring_test",
            marine_domain=True,
            terrestrial_domain=True,
            acquisition_framework=af,
        )
        db.session.add(jdd)

        monitoring_fixture["module"] = module
        monitoring_fixture["jdd"] = jdd
        monitoring_fixture["af"] = af

    return monitoring_fixture


@pytest.fixture
def mappings_field():
    mappings = {}
    with db.session.begin_nested():
        mapping = TMappingField(
            code="ref_geo.linear_group__test1",
            schema_code="ref_geo.linear_group",
            value={"id_type": "'RTE'", "code": "numero", "name": "CONCAT(cl_admin, ' ', numero)"},
        )
        db.session.add(mapping)
        mappings[mapping.code] = mapping

        mapping = TMappingField(
            code="ref_geo.linear__test1",
            schema_code="ref_geo.linear",
            value={
                "id_type": "'RTE'",
                "linear_code": "id",
                "linear_name": "CONCAT(numero, '_', substring(id, 9))",
                "geom": "wkt",
                "enable": True,
                "source": "https://geoservices.ign.fr/bdtopo#telechargementshpreg",
                "groups": "numero",
            },
        )
        db.session.add(mapping)
        mappings[mapping.code] = mapping

    return mappings
