import sqlalchemy as sa
from pypnusershub.db.models import User
from .models import PassageFaune, Actor
from geonature.utils.env import db


@classmethod
def passage_faune_subquery_scope(cls, id_role):
    CurrentUser = sa.orm.aliased(User)

    pre_scope = (
        db.session.query(PassageFaune)
        .join(CurrentUser, CurrentUser.id_role == id_role)
        .join(PassageFaune.actors, isouter=True)
        .with_entities(
            PassageFaune.id_passage_faune,
            PassageFaune.id_digitiser,
            PassageFaune.uuid_passage_faune,
            CurrentUser.id_organisme.label("id_organisme_cur"),
            CurrentUser.identifiant,
            Actor.id_organism.label("id_organisme_acteur"),
        )
        .cte("pre_scope")
    )
    scope_expression = db.session.query(PassageFaune).with_entities(
        PassageFaune.id_passage_faune,
        sa.case(
            [
                (PassageFaune.id_digitiser == id_role, 1),
                (
                    sa.exists().where(
                        sa.and_(
                            pre_scope.c.id_passage_faune == PassageFaune.id_passage_faune,
                            pre_scope.c.id_organisme_acteur == pre_scope.c.id_organisme_cur,
                        )
                    ),
                    2,
                ),
            ],
            else_=3,
        ).label("scope"),
    )

    return scope_expression


@classmethod
def passage_faune_permission_filter(cls, query, id_role, scope_for_action, sensitivity):
    if scope_for_action < 3:
        query = query.add_subquery_scope(id_role)
        return query._subquery_scope.c.scope <= scope_for_action, query
    else:
        return None, query


PassageFaune.subquery_scope = passage_faune_subquery_scope
PassageFaune.permission_filter = passage_faune_permission_filter
