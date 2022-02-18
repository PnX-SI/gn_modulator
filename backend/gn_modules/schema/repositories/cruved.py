'''
    method for cruved autorizations an d query filters
'''

from flask import g

from geonature.core.gn_meta.models import TDatasets
from geonature.core.gn_permissions.tools import (
    get_scopes_by_action
)

class SchemaRepositoriesCruved():
    '''
        methodes pour l'accès aux données
    '''

    def process_cruved(self, cruved_type, Model, query):
        '''
            check if user has access to data
            source
        '''

        if not self.attr('meta.check_cruved'):
            return query

        user_cruved = get_scopes_by_action(module_code="META_DATA")

        setattr(Model, 'cruved_ownership', self.cruved_ownership(g.current_user.id_role, g.current_user.id_organisme))

        query = query.filter(getattr(Model, 'cruved_ownership') <= user_cruved.get(cruved_type))

        return query
