'''
    SchemaMethods : api
'''

import json
import copy
from flask.views import MethodView
from flask import request, jsonify, Response, current_app
from functools import wraps
import csv
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

class Line(object):
    def __init__(self):
        self._line = None

    def write(self, line):
        self._line = line

    def read(self):
        return self._line


def iter_csv(data):
    line = Line()
    writer = csv.writer(line)
    for csv_line in data:
        writer.writerow(csv_line)
        yield line.read()

class SchemaApi():
    '''
        class for schema api processing

        doc:
          - https://flask.palletsprojects.com/en/2.0.x/views/

    '''

    def method_view_name(self, view_type=''):
        return self.attr('meta.method_view_name', 'MV{}{}'.format(view_type.title(), self.schema_name('pascal_case')))

    def view_name(self, view_type):
        '''
        '''
        return self.attr('meta.view_name', 'api_{}_{}'.format(view_type, self.schema_name('snake_case')))

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
            self.attr(
                'meta.url',
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
            - prefilters
            - fields
            - field_name
            - sorters
            - page
            - page_size

            TODO plusieurs possibilités pour le parametrage
            - par exemple au format tabulator ou autre ....
        '''

        # params_txt = request.args.get('params', '{}')
        # params = json.loads(params_txt)
        params = {
            'as_geojson': self.load_param(request.args.get('as_geojson', 'false')),
            'compress': self.load_param(request.args.get('compress', 'false')),
            'fields': self.load_array_param(request.args.get('fields')),
            'field_name':  self.load_param(request.args.get('field_name', 'null')),
            'filters': self.load_param(request.args.get('filters', '[]')),
            'prefilters': self.load_param(request.args.get('prefilters', '[]')),
            'page': self.load_param(request.args.get('page', 'null')),
            'page_size': self.load_param(request.args.get('page_size', 'null')),
            'sorters': self.load_param(request.args.get('sorters', '[]')),
            "value": self.load_param(request.args.get('value', 'null')),
            'as_csv': self.load_param(request.args.get('as_csv', 'false')),
        }

        return params

    def load_array_param(self, param):
        '''
            pour les cas ou params est une chaine de caractère séparée par des ','
        '''

        if not param:
            return []

        return param.split(',')



    def load_param(self, param):
        if param == 'undefined':
            return None

        # pour traiter les true false
        try:
            return json.loads(param)
        except Exception:
            return param

    def schema_api_dict(self):
        '''
        '''

        def get_page_number(self_mv, value):
            params = self.parse_request_args(request)
            return self.get_page_number(params, value)

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

            if value:
                try:
                    return get_one_rest(value)
                except SchemaUnsufficientCruvedRigth as e:
                    return f"Vous n'avez pas les droits suffisants pour accéder à cette requête (schema_name: {self.schema_name()}, module_code: {module_code})"

            else:
                return get_list_rest()

        def get_one_rest(value):
            params = self.parse_request_args(request)

            try:

                m = self.get_row(
                    value,
                    field_name=params.get('field_name'),
                )

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson'),
            )

        def get_list_rest():

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

            return out

        def get_export(self_mv, module_code, export_code):
            '''
            TODO
            pour l'instant csv
            ajouter json, geosjon, shape, etc...
            recupérer les paramètres de route depuis la config ???

            '''

            return f"export {module_code} {export_code}"

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

            if not out['data']:
                return '', 404
            data_csv = []
            keys = list(params.get('fields', out['data'][0].keys()))
            data_csv.append(self.process_csv_keys(keys))
            data_csv += [
                [
                    self.process_csv_data(key, d)
                    for key in keys
                ] for d in out['data']
            ]

            if params.get('as_csv') == 'test':
                return jsonify(data_csv)

            response = Response(iter_csv(data_csv), mimetype='text/csv')
            response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
            return response

        def post_rest(self_mv):

            data = request.get_json()
            params = self.parse_request_args(request)

            try:
                m = self.insert_row(data)

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

        def patch_rest(self_mv, value):

            data = request.get_json()
            params = self.parse_request_args(request)
            field_name = request.args.get('field_name')

            try:
                m, _ = self.update_row(value, data, field_name)

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

        def delete_rest(self_mv, value):

            field_name = request.args.get('field_name')
            params = self.parse_request_args(request)

            m = self.get_row(value, field_name=field_name)
            dict_out = self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

            try:
                self.delete_row(value, field_name=field_name)

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return dict_out

        return {
            'rest': {
                'get': permissions.login_required(get_rest),
                'post': permissions.login_required(post_rest),
                'patch': permissions.login_required(patch_rest),
                'delete': permissions.login_required(delete_rest)
            },
            'config': {
                'get': permissions.login_required(get_config)
            },
            'page_number': {
                'get': permissions.login_required(get_page_number)
            }
            # 'export': {
            #     'get': permissions.login_required(get_export)
            # }

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

    def register_api(self, bp, options={}):
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

        # get export
        # view_func_export = self.view_func('export')
        # bp.add_url_rule(self.url('/export/<string:module_code>/<string:export_code>'), view_func=view_func_export, methods=['GET'])

    def process_dict_path(self, d, dict_path):
        '''
            return dict or dict part according to path
            process error if needed
        '''

        if not dict_path:
            return d

        p_error = []
        out = copy.deepcopy(d)
        for p in dict_path.split('/'):
            if p:
                # gestion des indices des listes
                try:
                    p = int(p)
                except Exception:
                    pass
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

    @classmethod
    def init_routes(cls, blueprint):
        for schema_name, sm in cls.get_schema_cache(object_type='schema').items():
            sm.register_api(blueprint)

# except Exception as e:
    # print('Erreur durant la création des routes pour {} : {}'.format(schema_name, str(e)))
    # raise(e)
