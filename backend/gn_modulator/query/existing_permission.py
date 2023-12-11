from geonature.utils.env import db
from geonature.core.gn_synthese.models import Synthese
from geonature.core.gn_meta.models import (
    TDatasets,
    CorDatasetActor,
    CorAcquisitionFrameworkActor,
    TAcquisitionFramework,
    TDatasets,
)
from pypnusershub.db.models import User
import sqlalchemy as sa


@classmethod
def synthese_permission_filter(cls, query, id_role, scope_for_action, sensitivity):
    conditions = []

    # conditions sur le scope
    if scope_for_action < 3:
        query = query.add_subquery_scope(id_role)
        conditions.append(query._subquery_scope.c.scope <= scope_for_action)

    if sensitivity:
        conditions.append(
            Synthese.id_nomenclature_sensitivity
            == sa.func.ref_nomenclatures.get_id_nomenclature("SENSIBILITE", "0")
        )

    return sa.and_(*conditions), query


@classmethod
def synthese_subquery_scope(cls, id_role):
    Observers = sa.orm.aliased(User)
    CurrentUser = sa.orm.aliased(User)

    pre_scope = (
        db.session.query(Synthese)
        .join(CurrentUser, CurrentUser.id_role == id_role)
        .join(Observers, Synthese.cor_observers, isouter=True)
        .join(TDatasets, Synthese.dataset, isouter=True)
        .join(TDatasets.cor_dataset_actor, isouter=True)
        .join(TAcquisitionFramework, TDatasets.acquisition_framework, isouter=True)
        .join(TAcquisitionFramework.cor_af_actor, isouter=True)
        .with_entities(
            Synthese.id_synthese,
            Observers.id_role.label("id_role_obs"),
            Observers.id_organisme.label("id_organisme_obs"),
            CurrentUser.id_role.label("id_role_cur"),
            CurrentUser.id_organisme.label("id_organisme_cur"),
            CorDatasetActor.id_role.label("id_role_jdd"),
            CorDatasetActor.id_organism.label("id_organisme_jdd"),
            CorAcquisitionFrameworkActor.id_role.label("id_role_af"),
            CorAcquisitionFrameworkActor.id_organism.label("id_organisme_af"),
        )
    ).cte("pre_scope")

    scope_expression = db.session.query(Synthese).with_entities(
        Synthese.id_synthese,
        sa.case(
            [
                (
                    sa.or_(
                        Synthese.id_digitiser == id_role,
                        sa.exists().where(
                            sa.and_(
                                pre_scope.c.id_synthese == Synthese.id_synthese,
                                sa.or_(
                                    pre_scope.c.id_role_obs == pre_scope.c.id_role_cur,
                                    pre_scope.c.id_role_jdd == pre_scope.c.id_role_cur,
                                    pre_scope.c.id_role_af == pre_scope.c.id_role_cur,
                                ),
                            )
                        ),
                    ),
                    1,
                ),
                (
                    sa.or_(
                        sa.exists().where(
                            sa.and_(
                                pre_scope.c.id_synthese == Synthese.id_synthese,
                                sa.or_(
                                    pre_scope.c.id_organisme_obs == pre_scope.c.id_organisme_cur,
                                    pre_scope.c.id_organisme_jdd == pre_scope.c.id_organisme_cur,
                                    pre_scope.c.id_organisme_af == pre_scope.c.id_organisme_cur,
                                ),
                            )
                        )
                    ),
                    2,
                ),
            ],
            else_=3,
        ).label("scope"),
    )

    return scope_expression


Synthese.subquery_scope = synthese_subquery_scope
Synthese.permission_filter = synthese_permission_filter
