from .base import BaseSchemaQuery
from pypnusershub.db.models import User
import sqlalchemy as sa
from geonature.core.gn_permissions.tools import get_scopes_by_action
from geonature.utils.env import db
from sqlalchemy.sql import visitors


class SchemaQueryPermission(BaseSchemaQuery):
    def expression_scope(self, id_role):
        return self.Model().expression_scope(id_role)

    def add_subquery_scope(self, id_role):
        if hasattr(self, "has_subquery_scope"):
            return self
        Model = self.Model()
        subquery_scope = self.scope_query(id_role)
        subquery_scope = subquery_scope.cte("subquery_scope")

        self = self.join(
            subquery_scope,
            getattr(subquery_scope.c, Model.pk_field_name())
            == getattr(Model, Model.pk_field_name()),
        )
        self.has_attr_subquery_scope = True
        return self

    def scope_query(self, id_role):
        Model = self.Model()
        scope_query = Model.query
        scope_query = db.session.query(getattr(Model, Model.pk_field_name()))
        expression_scope = self.expression_scope(id_role)
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

        self = self.add_subquery_scope(id_role)
        self = self.add_columns("subquery_scope.scope AS scope")

        return self

    def process_permission_filter(self, cruved_type, module_code, id_role):
        """ """
        if id_role is None:
            return self

        user_cruved = get_scopes_by_action(id_role=id_role, module_code=module_code)

        cruved_for_type = user_cruved.get(cruved_type)

        if cruved_for_type < 3:
            self = self.filter(sa.text(f"subquery_scope.scope <= {cruved_for_type}"))

        return self
