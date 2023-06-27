"""
    method for cruved autorizations an d query filters
"""

from flask import g
from sqlalchemy import case, literal, or_

from geonature.core.gn_permissions.tools import get_scopes_by_action


class SchemaRepositoriesCruved:
    """
    methodes pour l'accès aux données

    TODO voire comment parametre les schema
    pour avoir différentes façon de calculer cruved scope
    """

    def expression_scope(self):
        Model = self.Model()

        if self.attr("meta.check_cruved") is None:
            return literal(0)
        else:
            return case(
                [
                    (
                        or_(
                            Model.actors.any(id_role=g.current_user.id_role),
                            Model.id_digitiser == g.current_user.id_role,
                        ),
                        1,
                    ),
                    (Model.actors.any(id_organism=g.current_user.id_organisme), 2),
                ],
                else_=3,
            )

    def add_column_scope(self, query):
        """
        ajout d'une colonne 'scope' à la requête
        afin de
            - filter dans la requete de liste
            - verifier les droit sur un donnée pour les action unitaire (post update delete)
            - le rendre accessible pour le frontend
                - affichage de boutton, vérification d'accès aux pages etc ....
        """

        query = query.add_columns(self.expression_scope().label("scope"))

        return query

    def process_cruved_filter(self, cruved_type, module_code, query):
        """ """

        if self.attr("meta.check_cruved") is None:
            return query

        if not hasattr(g, "current_user"):
            return query

        user_cruved = get_scopes_by_action(module_code=module_code)

        cruved_for_type = user_cruved.get(cruved_type)
        if cruved_for_type < 3:
            query = query.filter(self.expression_scope() <= cruved_for_type)

        return query
