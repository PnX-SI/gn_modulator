import sqlalchemy as sa
from pypnusershub.db.models import User
from .models import PassageFaune, Actor
from geonature.utils.env import db


def passage_faune_subquery_scope(self, id_role):
    CurrentUser = sa.orm.aliased(User)
    PassageFaune = self.Model()

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
    pre_scope_alias = sa.alias(pre_scope, name="pre_scope_main")
    scope_expression = (
        # sa.orm.select(pre_scope_alias)
        db.session.query(pre_scope_alias)
        # .join(PassageFaune, PassageFaune.id_passage_faune == pre_scope.c.id_passage_faune)
        .with_entities(
            pre_scope_alias.c.id_passage_faune,
            pre_scope_alias.c.uuid_passage_faune,
            pre_scope_alias.c.identifiant,
            sa.case(
                [
                    (pre_scope_alias.c.id_digitiser == id_role, 1),
                    (
                        sa.exists().where(
                            sa.and_(
                                pre_scope.c.id_passage_faune == pre_scope_alias.c.id_passage_faune,
                                pre_scope.c.id_organisme_acteur == pre_scope.c.id_organisme_cur,
                            )
                        ),
                        2,
                    ),
                ],
                else_=3,
            ).label("scope"),
        )
    )

    return scope_expression


def passage_faune_permission_filter(self, id_role, scope_for_action, sensitivity):
    if scope_for_action < 3:
        self = self.add_subquery_scope(id_role)
        return self._subquery_scope.c.scope <= scope_for_action, self
    else:
        return None, self


PassageFaune.query_class.subquery_scope = passage_faune_subquery_scope
PassageFaune.query_class.permission_filter = passage_faune_permission_filter
