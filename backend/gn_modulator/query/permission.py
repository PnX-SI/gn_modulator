import sqlalchemy as sa
from .base import BaseSchemaQuery
from geonature.core.gn_permissions.tools import get_scope
from geonature.core.gn_permissions.tools import get_permissions


class SchemaQueryPermission(BaseSchemaQuery):
    def add_subquery_scope(self, id_role):
        # test si la methode existe
        if not hasattr(self.Model(), "subquery_scope"):
            return self

        # test si la sous requete est deja ajoutée
        if hasattr(self, "_subquery_scope"):
            return self
        Model = self.Model()
        subquery_scope = Model.subquery_scope(id_role).cte("scope")

        self = self.join(
            subquery_scope,
            getattr(subquery_scope.c, Model.pk_field_name())
            == getattr(Model, Model.pk_field_name()),
        )
        self._subquery_scope = subquery_scope
        return self

    def add_column_scope(self, id_role):
        """
        ajout d'une colonne 'scope' à la requête
        afin de
            - filter dans la requete de liste
            - verifier les droit sur un donnée pour les action unitaire (post update delete)
            - le rendre accessible pour le frontend
                - affichage de boutton, vérification d'accès aux pages etc ....
        """

        if not hasattr(self.Model(), "subquery_scope"):
            self = self.add_columns(
                sa.sql.literal_column("0", type_=sa.sql.sqltypes.INTEGER).label("scope")
            )
        else:
            self = self.add_subquery_scope(id_role)
            self = self.add_columns(self._subquery_scope.c.scope)

        return self

    def process_filter_permission(self, id_role, action, module_code):
        if not id_role:
            return self

        if not hasattr(self.Model(), "permission_filter"):
            return self

        scope_for_action = get_scope(
            action, id_role=id_role, module_code=module_code, bypass_warning=True
        )

        permissions = get_permissions(action, id_role, module_code)
        sensitivity = any([perm.sensitivity_filter for perm in permissions])

        permission_filter, self = self.Model().permission_filter(
            self, id_role, scope_for_action, sensitivity
        )

        if permission_filter is not None:
            self = self.filter(permission_filter)

        return self
