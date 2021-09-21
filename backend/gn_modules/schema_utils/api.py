'''
    SchemaMethods : api
'''

import json

from flask.views import MethodView
from flask import request

from geonature.utils.config import config
from gn_modules import MODULE_CODE


class SchemaApi():
    '''
        class for schema api processing

        doc:
          - https://flask.palletsprojects.com/en/2.0.x/views/

    '''

    def method_view_name(self, view_type=''):
        '''
            returns model_name
            can be 
              - defined in self._schema['$meta']['model_name'] 
              - or retrieved from module_code and schema_name 'MV{full_name('pascal_case')}'
        '''
        return self._schema['$meta'].get('method_view_name', 'MV{}{}'.format(view_type.title(), self.full_name('pascal_case')))

    def view_name(self, view_type):
        '''
        '''
        return self._schema['$meta'].get('view_name', 'api_{}_{}'.format(view_type, self.full_name('snake_case')))

    def base_url(self):
        '''
        base url (may differ with apps (GN, UH, TH, ...))

        TODO process apps ?

        '''
        return '{}/{}'.format(config['API_ENDPOINT'], MODULE_CODE.lower())


    def url(self, pre_url, post_url='', full_url=False):
        '''
        /{pre_url}/{module_code}/{schema_name}{post_url}

        TODO gérer par type d'url ?
        '''

        url = (
            self._schema['$meta'].get(
                'url',
                '/{}/{}/{}{}'
                    .format(pre_url, self.module_code(), self.schema_name(), post_url)
                )
            )

        if full_url:
            url  = '{}{}'.format(self.base_url(), url)

        return url

    def parse_request_args_for_list(self, request):
        '''
            TODO !!! à refaire avec repo get_list
            parse request flask element
            - filters
            - sorters
            - page
            - size

            TODO plusieurs possibilités pour le parametrage 
            - par exemple au format tabulator ou autre ....
        '''

        params_txt = request.args.get('params', '{}');
        print(params_txt) 
        params = json.loads(params_txt)

        return params

    def schema_api_dict(self):
        '''
        '''
        def get_schema(self_mv, value=None):
            return self.schema()

        def get_config(self_mv, value=None):
            return self.config()

        def get_rest(self_mv, value=None):
            
            if value:
                # get one from id
                field_name = request.args.get('field_name')
                m = self.get_row(value, field_name)
                return self.serialize(m) 
            else:
                # get list
                params = self.parse_request_args_for_list(request)
                res_list = self.get_list(params).all()
                return {'data' : [self.serialize(r) for r in res_list]}

        def post_rest(self_mv):

            data = request.get_json()
            
            m = self.insert_row(data) 
            return self.serialize(m)

        def patch_rest(self_mv, value):
            
            data = request.get_json()
            field_name = request.args.get('field_name')
            
            m = self.update_row(value, data, field_name) 
            return self.serialize(m)

        def delete_rest(self_mv, value):

            field_name = request.args.get('field_name')
            
            m = self.delete_row(value, field_name)
            return self.serialize(m)

        return {
            'rest': {
                'get': get_rest,
                'post': post_rest,
                'patch': patch_rest,
                'delete': delete_rest,
            },
            'config': {
                'get': get_config,
            },
            'schema': {
                'get': get_schema,
            }
        }

    def view_func(self, view_type):
        MV = type(
            self.method_view_name(view_type),
            (MethodView,),
            self.schema_api_dict()[view_type]
        )
        return MV.as_view(self.view_name(view_type))

    def register_api(self, bp):
        '''
            Fonction qui enregistre une api pour un schema

            TODO s
                -comment gérer la config pour limiter les routes selon le cruved
        '''

        # rest api
        view_func_rest = self.view_func('rest')
        bp.add_url_rule(self.url('rest', 's/'), defaults={'value': None}, view_func=view_func_rest, methods=['GET'])
        bp.add_url_rule(self.url('rest', 's/'), view_func=view_func_rest, methods=['POST'])
        bp.add_url_rule(self.url('rest', 's/<value>'), view_func=view_func_rest, methods=['GET', 'PATCH', 'DELETE'])

        # config, schema
        for view_type in ['config', 'schema']:
            bp.add_url_rule(
                self.url(view_type),
                view_func=self.view_func(view_type),
                methods=['GET']
            )

