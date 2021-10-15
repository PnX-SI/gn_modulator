'''
    SchemaMethods : api
'''

import json

from flask.views import MethodView
from flask import request, jsonify

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
              - or retrieved from group_name and object_name 'MV{full_name('pascal_case')}'
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


    def url(self, post_url, full_url=False):
        '''
        /{group_name}/{object_name}{post_url}

        - full/url renvoie l'url complet

        TODO gérer par type d'url ?
        '''

        url = (
            self._schema['$meta'].get(
                'url',
                '/{}/{}{}'
                    .format(self.group_name(), self.object_name(), post_url)
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
        params = json.loads(params_txt)

        return params

    def schema_api_dict(self):
        '''
        '''


        def get_schema(self_mv, schema_path):
            '''
                return schema or shema part

                schema_path : 'elem1.elem2' => return schema['elem1']['elem2']
            '''
            out = self._schema
            if not schema_path:
                return out
            for p in schema_path.split('.'):
                out = out[p]
            return out

        def get_config(self_mv, config_path):
            '''
                return config or config part

                config_path : 'elem1.elem2' => return schema['elem1']['elem2']
            '''
            out = self.config()
            if not config_path:
                return out
            for p in config_path.split('.'):
                out = out[p]

            return jsonify(out)

        def get_rest(self_mv, value=None):

            # get one from id
            if value:

                field_name = request.args.get('field_name')
                m = self.get_row(value, field_name).one()
                return self.serialize(m)


            # get list
            else:
                import time, math
                t = time.time()
                # do stuff
                params = self.parse_request_args_for_list(request)
                query, query_info = self.get_list(params)
                res_list = query.all()
                print('query', round(time.time() - t, 4))
                t = time.time()

                out = {
                    **query_info,
                    # 'data' : [self.serialize2(r, params.get('fields', [])) for r in res_list]
                    'data' : self.serialize_list(res_list, params.get('fields', []))
                }
                print('serial', round(time.time() - t, 4))
                t = time.time()

                return out

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

            m = self.get_one(value, field_name).one()
            dict_out = self.serialize(m)
            self.delete_row(value, field_name)
            return dict_out

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
        bp.add_url_rule(self.url('/rest/'), defaults={'value': None}, view_func=view_func_rest, methods=['GET'])
        bp.add_url_rule(self.url('/rest/'), view_func=view_func_rest, methods=['POST'])
        bp.add_url_rule(self.url('/rest/<value>'), view_func=view_func_rest, methods=['GET', 'PATCH', 'DELETE'])

        # config
        view_func_config =self.view_func('config')
        bp.add_url_rule(self.url('/config/'), defaults={'config_path': None}, view_func=view_func_config, methods=['GET'])
        bp.add_url_rule(self.url('/config/<config_path>'), view_func=view_func_config, methods=['GET'])

        # # schema
        view_func_schema =self.view_func('schema')
        bp.add_url_rule(self.url('/schema/'), defaults={'schema_path': None}, view_func=view_func_schema, methods=['GET'])
        bp.add_url_rule(self.url('/schema/<schema_path>'), view_func=view_func_schema, methods=['GET'])
