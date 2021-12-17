'''
    method for cruved autorizations an d query filters
'''

from geonature.core.gn_meta.models import TDatasets


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

        # variables field_names
        # can be redefined in schema#$meta

        id_dataset_field_name = self.meta('check_cruved.id_dataset_field_name', 'id_dataset')

        # dataset
        allowed_datasets = [
            d.id_dataset for d in TDatasets.query.filter_by_scope(int(info_role.value_filter)).all()
        ]

        # TODO add cond for dataset test
        query = query.filter(getattr(Model, id_dataset_field_name).in_(allowed_datasets))


        # owner


        # organisme

        return query
