import sqlalchemy as sa
from pypnusershub.db.models import User
from .models import PassageFaune, Actor, Diagnostic
from geonature.utils.env import db
from gn_modulator.query.permission import add_subquery_scope


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
            else_=3,
        ).label("scope"),
    )

    return scope_expression


@classmethod
def passage_faune_permission_filter(cls, query, id_role, scope_for_action, sensitivity):
    if scope_for_action < 3:
        query = add_subquery_scope(cls, query, id_role)
        return query._subquery_scope.c.scope <= scope_for_action, query
    else:
        return None, query


@classmethod
def diagnostic_subquery_scope(cls, id_role):
    scope_expression_passage_faune = PassageFaune.subquery_scope(id_role).cte("pre_scope_pf")
    scope_expression = (
        db.session.query(Diagnostic)
        .join(
            scope_expression_passage_faune,
            scope_expression_passage_faune.c.id_passage_faune == Diagnostic.id_passage_faune,
        )
        .with_entities(Diagnostic.id_diagnostic, scope_expression_passage_faune.c.scope)
    )

    return scope_expression


@classmethod
def diagnostic_permission_filter(cls, query, id_role, scope_for_action, sensitivity):
    if scope_for_action < 3:
        query = add_subquery_scope(cls, query, id_role)
        return query._subquery_scope.c.scope <= scope_for_action, query
    else:
        return None, query


PassageFaune.subquery_scope = passage_faune_subquery_scope
PassageFaune.permission_filter = passage_faune_permission_filter


Diagnostic.subquery_scope = diagnostic_subquery_scope
Diagnostic.permission_filter = diagnostic_permission_filter
