from .base import BaseSchemaQuery
from pypnusershub.db.models import User
import sqlalchemy as sa
from geonature.core.gn_permissions.tools import get_scopes_by_action
from geonature.utils.env import db
from sqlalchemy.sql import visitors

from geonature.core.gn_synthese.models import Synthese
from geonature.core.gn_meta.models import TDatasets


class SchemaQueryPermission(BaseSchemaQuery):
    def check_cruved(self):
        return hasattr(self.Model(), "expression_scope")

    def add_subquery_scope(self, id_role):
        if hasattr(self, "has_subquery_scope"):
            return self
        Model = self.Model()
        subquery_scope = self.scope_query(id_role)
        subquery_scope = subquery_scope.cte("sq_scope")

        self = self.join(
            subquery_scope,
            getattr(subquery_scope.c, Model.pk_field_name())
            == getattr(Model, Model.pk_field_name()),
        )
        self.has_subquery_scope = True
        return self

    def scope_query(self, id_role):
        Model = self.Model()
        scope_query = Model.query

        # requete de base
        scope_query = db.session.query(getattr(Model, Model.pk_field_name()))

        # colonne scope
        # expression du scope portée par le modèle
        expression_scope, scope_query = self.Model().expression_scope(scope_query, id_role)
        scope_query = scope_query.add_columns(expression_scope.label("scope"))
        return scope_query

    def add_column_scope(self, id_role):
        """
        ajout d'une colonne 'scope' à la requête
        afin de
            - filter dans la requete de liste
            - verifier les droit sur un donnée pour les action unitaire (post update delete)
            - le rendre accessible pour le frontend
                - affichage de boutton, vérification d'accès aux pages etc ....
        """

        if not self.check_cruved():
            self.add_columns("0 as scope")
        else:
            self = self.add_subquery_scope(id_role)
            self = self.add_columns("scope")

        return self

    def process_permission_filter(self, cruved_type, module_code, id_role):
        """ """
        print("permission_filter", id_role, self.check_cruved())
        # pas de vérification de permission sans id_role
        if id_role is None:
            return self

        if self.check_cruved():
            user_cruved = get_scopes_by_action(id_role=id_role, module_code=module_code)
            cruved_for_type = user_cruved.get(cruved_type)
            print(cruved_for_type)
            if cruved_for_type < 3:
                self = self.add_subquery_scope(id_role)
                self = self.filter(sa.text(f"sq_scope.scope <= {cruved_for_type}"))

        # autres permissions sensibilité etc ...
        return self


@classmethod
def synthese_expression_scope(cls, query, id_role):
    # scope 1 si
    # digitiser
    # dans les observateur
    # dans les jdd

    # query = query.join(User, User.id_role == id_role)
    # cond_scope_2 = (
    #     sa.or_(
    #         Synthese.cor_observers.any(id_organisme=User.id_organisme),
    #         sa.and_(
    #             Synthese.id_dataset == TDatasets.id_dataset,
    #             TDatasets.user_actors.any(id_organisme=User.id_organisme),
    #         ),
    #     ),
    # )

    # scope 2 si
    # observateur de meme org
    # jdd avec obs de meme org
    CurrentUser = sa.orm.aliased(User)
    query = query.join(CurrentUser)
    scope_expression = sa.case(
        [
            # scope 1 utilisateur
            (
                sa.or_(
                    Synthese.id_digitiser == id_role,
                    Synthese.cor_observers.any(User.id_role == id_role),
                    sa.and_(
                        Synthese.id_dataset == TDatasets.id_dataset,
                        TDatasets.cor_dataset_actor.any(User.id_role == id_role),
                    ),
                ),
                1,
            ),
            # scope 2 organisme
            (
                sa.or_(
                    Synthese.cor_observers.any(User.id_organisme == CurrentUser.id_organisme),
                    sa.and_(
                        Synthese.id_dataset == TDatasets.id_dataset,
                        TDatasets.cor_dataset_actor.any(
                            User.id_organisme == CurrentUser.id_organisme
                        ),
                    ),
                ),
                1,
            ),
        ],
        else_=3,
    )

    return scope_expression, query


Synthese.expression_scope = synthese_expression_scope
print("S", Synthese.expression_scope)
