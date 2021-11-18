'''
    SchemaMethods : api
'''

import json
import copy
from flask.views import MethodView
from flask import request, jsonify

from geonature.utils.config import config
from gn_modules import MODULE_CODE

from .errors import SchemaLoadError

class SchemaApi():
    '''
        class for schema api processing

        doc:
          - https://flask.palletsprojects.com/en/2.0.x/views/

    '''

    def method_view_name(self, view_type=''):
        return self.meta('method_view_name', 'MV{}{}'.format(view_type.title(), self.schema_name('pascal_case')))

    def view_name(self, view_type):
        '''
        '''
        return self.meta('view_name', 'api_{}_{}'.format(view_type, self.schema_name('snake_case')))

    def base_url(self):
        '''
        base url (may differ with apps (GN, UH, TH, ...))

        TODO process apps ?

        '''
        return '{}/{}'.format(config['API_ENDPOINT'], MODULE_CODE.lower())

    def url(self, post_url, full_url=False):
        '''
        /{schema_name}{post_url}

        - full/url renvoie l'url complet

        TODO gérer par type d'url ?
        '''

        url = (
            self.meta(
                'url',
                '/{}{}'.format(self.schema_name(), post_url)
            )
        )

        if full_url:
            url = '{}{}'.format(self.base_url(), url)

        return url

    def parse_request_args(self, request):
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

        # params_txt = request.args.get('params', '{}')
        # params = json.loads(params_txt)
        params = {
            'size': self.load_param(request.args.get('size', 'null')),
            'page': self.load_param(request.args.get('page', 'null')),
            'filters': self.load_param(request.args.get('filters', '[]')),
            'sorters': self.load_param(request.args.get('sorters', '[]')),
            'fields': self.load_param(request.args.get('fields', '[]')),
            'as_geojson': self.load_param(request.args.get('as_geojson', 'false')),
            'compress': self.load_param(request.args.get('compress', 'false')),
        }
        return params

    def load_param(self, param):
        if param == 'undefined':
            return None
        return json.loads(param)

    def schema_api_dict(self):
        '''
        '''

        def get_config(self_mv, config_path):
            '''
                return config or config part

                config_path : 'elem1/elem2' => return config['elem1']['elem2']
            '''
            config = None

            # gerer les erreurs de config
            try:
                config = self.config()
            except SchemaLoadError as e:
                return str(e), 500
            return self.process_dict_path(config, config_path)

        def get_rest(self_mv, value=None):
            self.reload()
            # get one from id
            if value:

                params = self.parse_request_args(request)
                m = self.get_row(
                    value,
                    field_name=params.get('field_name'),
                )

                return self.serialize(
                    m,
                    fields=params.get('fields'),
                    as_geojson=params.get('as_geojson'),
                )

            # get list
            else:
                params = self.parse_request_args(request)
                query, query_info = self.get_list(params)
                res_list = query.all()

                out = {
                    **query_info,
                    'data': self.serialize_list(
                        res_list,
                        fields=params.get('fields'),
                        as_geojson=params.get('as_geojson'),
                    )
                }

                if params.get('compress'):
                    out['fields'] = params.get('fields')
                    data = []
                    for d in out['data']:
                        dd = [d[f] for f in out['fields'] if f != 'geom']
                        dd += [
                            d[self.geometry_field_name()]['coordinates'][0],
                            d[self.geometry_field_name()]['coordinates'][1]
                        ]
                        data.append(dd)
                    out['fields'] += ['x', 'y']
                    out['fields'].remove(self.geometry_field_name())
                    out['data'] = data
                return out

        def post_rest(self_mv):

            data = request.get_json()

            m = self.insert_row(data)
            return self.serialize(m)

        def patch_rest(self_mv, value):

            self.reload()
            data = request.get_json()
            field_name = request.args.get('field_name')

            m, is_new = self.update_row(value, data, field_name)
            return self.serialize(m)

        def delete_rest(self_mv, value):

            field_name = request.args.get('field_name')

            m = self.get_row(value, field_name=field_name)
            dict_out = self.serialize(m)
            self.delete_row(value, field_name=field_name)
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
            }        }

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
        view_func_config = self.view_func('config')
        bp.add_url_rule(self.url('/config/'), defaults={'config_path': None}, view_func=view_func_config, methods=['GET'])
        bp.add_url_rule(self.url('/config/<path:config_path>'), view_func=view_func_config, methods=['GET'])

    def process_dict_path(self, d, dict_path):
        '''
            return dict or dict part according to path
            process error if needed
        '''

        if not dict_path:
            return d

        p_error = []
        out = copy.copy(d)
        for p in dict_path.split('/'):
            if p:
                try:
                    out = out[p]
                    p_error.append(p)
                except Exception:
                    path_error = '/'.join(p_error)
                    txt_error = "La chemin demandé <b>{}/{}</b> n'est pas correct\n".format(path_error, p)
                    if type(out) is dict and out.keys():
                        txt_error += "<br><br>Vous pouvez choisir un chemin parmi :"
                        for key in out:
                            url_key = self.url('/config/' + path_error + "/" + key, full_url=True)
                            txt_error += '<br> - <a href="{}">{}{}</a>'.format(url_key, path_error + '/' if path_error else '', key)
                    return txt_error, 500

        return jsonify(out)

