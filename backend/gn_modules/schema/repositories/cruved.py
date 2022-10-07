'''
    method for cruved autorizations an d query filters
'''

from flask import g

from sqlalchemy import func, select, case, exists, and_ , literal_column, cast, column, text, literal

from geonature.core.gn_meta.models import TDatasets
from geonature.core.gn_permissions.tools import (
    get_scopes_by_action
)

class SchemaRepositoriesCruved():
    '''
        methodes pour l'accès aux données

        TODO voire comment parametre les schema
        pour avoir différentes façon de calculer cruved ownership
    '''

    def expression_ownership(self):

        Model = self.Model()

        if self.attr('meta.check_cruved') is None:
            return literal(0)
        else:

            return case(
                [
                    (Model.actors.any(id_role=g.current_user.id_role), 1),
                    (Model.actors.any(id_organism=g.current_user.id_organisme), 2),
                ],
                else_=3
            )

    def add_column_ownership(self, query):
        '''
            ajout d'une colonne 'ownership' à la requête
            afin de
                - filter dans la requete de liste
                - verifier les droit sur un donnée pour les action unitaire (post update delete)
                - le rendre accessible pour le frontend
                    - affichage de boutton, vérification d'accès aux pages etc ....
        '''

        query = query.add_columns(self.expression_ownership().label('ownership'))

        return query


    def process_cruved_filter(self, cruved_type, module_code, query):
        '''
        '''

        if not hasattr(g, 'current_user'):
            return query



        user_cruved = get_scopes_by_action(module_code=module_code)

        query = query.filter(self.expression_ownership() <= user_cruved.get(cruved_type))

        return query
