from .base import BaseSchemaQuery
from pypnusershub.db.models import User
import sqlalchemy as sa
from geonature.core.gn_permissions.tools import get_scopes_by_action


class SchemaQueryPermission(BaseSchemaQuery):
    def expression_scope(self, id_role):
        Model = self.Model()

        if not id_role:
            return sa.literal(0)
        else:
            id_organism = User.query.filter_by.one(id_role=id_role).one().id_organism
            return sa.case(
                [
                    (
                        sa.or_(
                            Model.actors.any(id_role=id_role),
                            Model.id_digitiser == id_role,
                        ),
                        1,
                    ),
                    (Model.actors.any(id_organism=id_organism), 2),
                ],
                else_=3,
            )

    def add_column_scope(self, id_role):
        """
        ajout d'une colonne 'scope' à la requête
        afin de
            - filter dans la requete de liste
            - verifier les droit sur un donnée pour les action unitaire (post update delete)
            - le rendre accessible pour le frontend
                - affichage de boutton, vérification d'accès aux pages etc ....
        """

        self = self.add_columns(self.expression_scope(id_role).label("scope"))

        return self

    def process_permission_filter(self, cruved_type, module_code, id_role):
        """ """

        if id_role is None:
            return self

        user_cruved = get_scopes_by_action(module_code=module_code)

        cruved_for_type = user_cruved.get(cruved_type)

        if cruved_for_type < 3:
            self = self.filter(self.expression_scope() <= cruved_for_type)

        return self
