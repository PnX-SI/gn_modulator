'''
    SchemaMethods : api
'''

import json
import copy
from flask.views import MethodView
from flask import request, jsonify
from functools import wraps

from geonature.core.gn_permissions import decorators as permissions
from geonature.utils.config import config

from gn_modules import MODULE_CODE

from .errors import SchemaLoadError, SchemaUnsufficientCruvedRigth


# def check_cruved_on_row(view):
#     '''
#         decorator for
#     '''

#     @wraps(view)
#     def _check_cruved_on_row(*args, **kwargs):

#         try:
#             return view(*args, **kwargs)
#         except SchemaUnsufficientCruvedRigth as e:
#             return 'Erreur Cruved : {}'.format(str(e))

#     return _check_cruved_on_row

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
            'as_geojson': self.load_param(request.args.get('as_geojson', 'false')),
            'compress': self.load_param(request.args.get('compress', 'false')),
            'fields': self.load_param(request.args.get('fields', '[]')),
            'filters': self.load_param(request.args.get('filters', '[]')),
            'page': self.load_param(request.args.get('page', 'null')),
            'size': self.load_param(request.args.get('size', 'null')),
            'sorters': self.load_param(request.args.get('sorters', '[]')),
            "value": self.load_param(request.args.get('value', 'null'))
        }
        return params

    def load_param(self, param):
        if param == 'undefined':
            return None
        return json.loads(param)

    def schema_api_dict(self):
        '''
        '''

        def get_page_number(self_mv, info_role, value):
            params = self.parse_request_args(request)
            return self.get_page_number(params, value, info_role)

        def get_config(self_mv, config_path):
            '''
                return config or config part

                config_path : 'elem1/elem2' => return config['elem1']['elem2']
            '''

            if request.args.get('reload'):
                self.reload()
            config = None

            # gerer les erreurs de config
            try:
                config = self.config()
            except SchemaLoadError as e:
                return str(e), 500
            return self.process_dict_path(config, config_path)

        def get_rest(self_mv, info_role, value=None):

            if value:

                params = self.parse_request_args(request)

                try:

                    m = self.get_row(
                        value,
                        info_role=info_role,
                        field_name=params.get('field_name'),
                    )

                except SchemaUnsufficientCruvedRigth as e:
                    return 'Erreur Cruved : {}'.format(str(e)), 403

                return self.serialize(
                    m,
                    fields=params.get('fields'),
                    as_geojson=params.get('as_geojson'),
                )

            # get list
            else:
                params = self.parse_request_args(request)
                query, query_info = self.get_list(params, info_role)
                res_list = query.all()

                out = {
                    **query_info,
                    'data': self.serialize_list(
                        res_list,
                        fields=params.get('fields'),
                        as_geojson=params.get('as_geojson'),
                    )
                }

                # TODO à passer dans serializer
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

        def post_rest(self_mv, info_role):

            data = request.get_json()
            params = self.parse_request_args(request)

            try:
                m = self.insert_row(data, info_role=info_role)

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

        def patch_rest(self_mv, info_role, value):

            data = request.get_json()
            params = self.parse_request_args(request)
            field_name = request.args.get('field_name')

            try:
                m, _ = self.update_row(value, data, field_name, info_role=info_role)

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

        def delete_rest(self_mv, info_role, value):

            field_name = request.args.get('field_name')
            params = self.parse_request_args(request)

            m = self.get_row(value, field_name=field_name, info_role=info_role)
            dict_out = self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

            try:
                self.delete_row(info_role, value, field_name=field_name)

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return dict_out

        return {
            'rest': {
                'get': permissions.check_cruved_scope('R', True)(get_rest),
                'post': permissions.check_cruved_scope('C', True)(post_rest),
                'patch': permissions.check_cruved_scope('U', True)(patch_rest),
                'delete': permissions.check_cruved_scope('D', True)(delete_rest)
            },
            'config': {
                'get': permissions.check_cruved_scope('R')(get_config)
            },
            'page_number': {
                'get': permissions.check_cruved_scope('R', True)(get_page_number)
            }

        }

    def view_func(self, view_type):
        '''
            c'est ici que ce gère le CRUVED pour l'accès aux routes
        '''

        view_func = self.schema_api_dict()[view_type]

        MV = type(
            self.method_view_name(view_type),
            (MethodView,),
            view_func
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

        # page_number
        view_func_page_number = self.view_func('page_number')
        bp.add_url_rule(self.url('/page_number/<value>'), view_func=view_func_page_number, methods=['GET'])

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
                        for key in sorted(list(out.keys())):
                            url_key = self.url('/config/' + path_error + "/" + key, full_url=True)
                            txt_error += '<br> - <a href="{}">{}{}</a>'.format(url_key, path_error + '/' if path_error else '', key)
                    return txt_error, 500

        return jsonify(out)
