'''
    method for cruved autorizations an d query filters
'''

from geonature.core.gn_meta.models import TDatasets
from flask import g

class SchemaRepositoriesCruved():
    '''
        methodes pour l'accès aux données
    '''

    def process_cruved(self, info_role, cruved_type, Model, query):
        '''
            check if user has access to data
            source
        '''

        if not self.meta('check_cruved'):
            return query

        setattr(Model, 'cruved_ownership', self.cruved_ownership(g.current_user.id_role, g.current_user.id_organisme))
        query = query.filter(getattr(Model, 'cruved_ownership') <= info_role.value_filter)

        return query
