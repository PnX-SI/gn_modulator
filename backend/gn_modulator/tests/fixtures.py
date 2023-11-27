import pytest
import datetime
from geonature.utils.env import db
from m_sipaf.models import PassageFaune, Diagnostic, Actor
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from pypnusershub.db.models import Organisme
from geonature.core.gn_synthese.models import TSources, Synthese
from sqlalchemy import func
from apptax.taxonomie.models import Taxref
from geonature.core.gn_commons.models import TModules, TMedias, BibTablesLocation
from pypnnomenclature.repository import get_nomenclature_id_term
from geonature.core.gn_permissions.models import (
    PermFilterType,
    PermAction,
    PermObject,
    Permission,
)
from pypnusershub.db.models import (
    User,
    Organisme,
    Application,
    Profils as Profil,
    UserApplicationRight,
)

from flask import g


@pytest.fixture
def permission_cache():
    if not hasattr(g, "_permissions"):
        g._permissions = {}
    if not hasattr(g, "_permissions_by_user"):
        g._permissions_by_user = {}


@pytest.fixture
def passages_faune_with_diagnostic(users):
    point = Point(5.486786, 42.832182)
    geom = from_shape(point, srid=4326)
    uuids = ["0c92af92-000b-401c-9994-f2c12470493a", "0c92af92-000b-401c-9994-f2c12470493b"]
    passages_faune = []
    with db.session.begin_nested():
        for uuid in uuids:
            pf = PassageFaune(geom=geom, uuid_passage_faune=uuid)
            db.session.add(pf)
            organisme = Organisme.query.filter_by(nom_organisme="ALL").one()
            pf.diagnostics.append(
                Diagnostic(
                    id_organisme=organisme.id_organisme, date_diagnostic="2017-01-08 20:00:00.000"
                )
            )
            if uuid == "0c92af92-000b-401c-9994-f2c12470493a":
                pf.actors.append(
                    Actor(
                        id_organism=users["user"].id_organisme,
                        id_nomenclature_type_actor=get_nomenclature_id_term(
                            "PF_TYPE_ACTOR", "PRO"
                        ),
                    )
                )
            passages_faune.append(pf)
    return passages_faune


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
        db.session.add(
            Synthese(
                id_source=source.id_source,
                nom_cite=taxon.lb_nom,
                cd_nom=taxon.cd_nom,
                date_min=now,
                date_max=now,
                the_geom_4326=geom,
                the_geom_point=geom,
                the_geom_local=func.st_transform(geom, 2154),
            )
        )


@pytest.fixture(scope="session")
def users(app):
    app = Application.query.filter(Application.code_application == "GN").one()
    profil = Profil.query.filter(Profil.nom_profil == "Lecteur").one()

    modules = TModules.query.all()

    actions = {code: PermAction.query.filter_by(code_action=code).one() for code in "CRUVED"}

    def create_user(username, organisme=None, scope=None, sensitivity_filter=False):
        # do not commit directly on current transaction, as we want to rollback all changes at the end of tests
        with db.session.begin_nested():
            user = User(
                groupe=False,
                active=True,
                organisme=organisme,
                identifiant=username,
                password=username,
            )
            db.session.add(user)
        # user must have been commited for user.id_role to be defined
        with db.session.begin_nested():
            # login right

            right = UserApplicationRight(
                id_role=user.id_role, id_application=app.id_application, id_profil=profil.id_profil
            )
            db.session.add(right)
            if scope > 0:
                object_all = PermObject.query.filter_by(code_object="ALL").one()
                for action in actions.values():
                    for module in modules:
                        for obj in [object_all] + module.objects:
                            permission = Permission(
                                role=user,
                                action=action,
                                module=module,
                                object=obj,
                                scope_value=scope if scope != 3 else None,
                                sensitivity_filter=sensitivity_filter,
                            )
                            db.session.add(permission)
        return user

    users = {}

    organisme = Organisme(nom_organisme="test imports")
    db.session.add(organisme)

    users_to_create = [
        ("noright_user", organisme, 0),
        ("stranger_user", None, 2),
        ("associate_user", organisme, 2),
        ("self_user", organisme, 1),
        ("user", organisme, 2),
        ("admin_user", organisme, 3),
        ("associate_user_2_exclude_sensitive", organisme, 2, True),
    ]

    for username, *args in users_to_create:
        users[username] = create_user(username, *args)

    return users
