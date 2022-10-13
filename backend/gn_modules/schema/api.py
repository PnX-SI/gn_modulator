'''
    SchemaMethods : api
'''

import json
import copy
from flask.views import MethodView
from flask import request, jsonify, Response, current_app
from functools import wraps
import csv
import math
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

    @classmethod
    def base_url(cls):
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
            url = '{}{}'.format(self.cls.base_url(), url)

        return url

    def parse_request_args(self, request, options={}):
        '''
            TODO !!! à refaire avec repo get_list
            parse request flask element
            - filters
            - prefilters
            - fields
            - field_name
            - sort
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
            'filters': self.parse_filters(request.args.get('filters')),
            'prefilters': self.parse_filters(request.args.get('prefilters')),
            'page': self.load_param(request.args.get('page', 'null')),
            'page_size': self.load_param(request.args.get('page_size', 'null')),
            'sort': self.load_array_param(request.args.get('sort')),
            "value": self.load_param(request.args.get('value', 'null')),
            'as_csv': self.load_param(request.args.get('as_csv', 'false')),
            'cruved_type': self.load_param(request.args.get('cruved_type', 'null'))
        }

        if 'prefilters' in options:
            params['prefilters'] = (
                self.parse_filters(options['prefilters'])
                +
                params['prefilters']
            )

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

    def schema_api_dict(self, module_code, options):
        '''
        options : dict
            - prefilters
        '''


        def get_rest(self_mv, value=None):

            if value:
                try:
                    return get_one_rest(value)
                except SchemaUnsufficientCruvedRigth as e:
                    return f"Vous n'avez pas les droits suffisants pour accéder à cette requête (schema_name: {self.schema_name()}, module_code: {module_code})"

            else:
                return get_list_rest()

        def get_one_rest(value):
            params = self.parse_request_args(request, options)

            try:
                m = self.get_row(
                    value,
                    field_name=params.get('field_name'),
                    module_code=module_code,
                    cruved_type='R',
                    params=params
                ).one()

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson'),
            )

        def get_list_rest():

            params = self.parse_request_args(request, options)
            count_total = (
                self.query_list(
                    module_code=module_code,
                    cruved_type='R',
                    params=params,
                    query_type='total')
                .count()
            )

            count_filtered = (
                self.query_list(
                    module_code=module_code,
                    cruved_type='R',
                    params=params,
                    query_type='filtered')
                .count()
            )

            query_info = {
                'page': params.get('page') or 1,
                'page_size': params.get('page_size', None),
                'total': count_total,
                'filtered': count_filtered,
                'last_page': (
                    math.ceil(count_total / params.get('page_size'))
                    if params.get('page_size')
                    else 1
                )
            }

            query_list = self.query_list(
                module_code=module_code,
                cruved_type=params.get('cruved_type') or 'R',
                params=params
            )

            res_list = query_list.all()
            out = {
                **query_info,
                'data': self.serialize_list(
                    res_list,
                    fields=params.get('fields'),
                    as_geojson=params.get('as_geojson'),
                )
            }

            return out

        def post_rest(self_mv):

            data = request.get_json()
            params = self.parse_request_args(request, options)

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
            params = self.parse_request_args(request, options)

            try:
                m, _ = self.update_row(
                    value,
                    data,
                    field_name=params.get('field_name'),
                    module_code=module_code,
                    params=params
                )

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

        def delete_rest(self_mv, value):

            params = self.parse_request_args(request, options)

            m = self.get_row(
                value,
                field_name=params.get('field_name'),
                module_code=module_code,
                cruved_type='D',
                params = params
            ).one()
            dict_out = self.serialize(
                m,
                fields=params.get('fields'),
                as_geojson=params.get('as_geojson')
            )

            try:
                self.delete_row(value, field_name=params.get('field_name'))

            except SchemaUnsufficientCruvedRigth as e:
                return 'Erreur Cruved : {}'.format(str(e)), 403

            return dict_out

        def get_page_number(self_mv, value):
            '''
            '''

            params = self.parse_request_args(request, options)
            return {
                'page': self.get_page_number(
                    value,
                    module_code,
                    params.get('cruved_type') or 'R',
                    params
                )
            }


        return {
            'rest': {
                'get': permissions.check_cruved_scope('R', module_code=module_code)(get_rest),
                'post': permissions.check_cruved_scope('C', module_code=module_code)(post_rest),
                'patch': permissions.check_cruved_scope('U', module_code=module_code)(patch_rest),
                'delete': permissions.check_cruved_scope('D', module_code=module_code)(delete_rest)
            },
            'page_number': {
                'get': permissions.check_cruved_scope('R', module_code=module_code)(get_page_number)
            }
        }

    def schema_view_func(self, view_type, module_code, options):
        '''
            c'est ici que ce gère le CRUVED pour l'accès aux routes
        '''

        schema_api_dict = self.schema_api_dict(module_code, options)[view_type]

        MV = type(
            self.method_view_name(view_type),
            (MethodView,),
            schema_api_dict
        )
        return MV.as_view(self.view_name(view_type))

    def register_api(self, bp, module_code, object_name, options={}):
        '''
            Fonction qui enregistre une api pour un schema

            TODO s
                -comment gérer la config pour limiter les routes selon le cruved
        '''

        cruved = options.get('cruved', '')

        # rest api
        view_func_rest = self.schema_view_func('rest', module_code, options)
        view_func_page_number = self.schema_view_func('page_number', module_code, options)

        methods = []

        # read: GET (liste et one_row)
        if 'R' in cruved:
            bp.add_url_rule(f'/{object_name}/', defaults={'value': None}, view_func=view_func_rest, methods=['GET'])
            bp.add_url_rule(f'/{object_name}/<value>', view_func=view_func_rest, methods=['GET'])
            bp.add_url_rule(f'/{object_name}/page_number/<value>', view_func=view_func_page_number, methods=['GET'])

        # create : POST
        if 'C' in cruved:
            bp.add_url_rule(f'/{object_name}/', view_func=view_func_rest, methods=['POST'])

        # update : PATCH
        if 'U' in cruved:
            bp.add_url_rule(f'/{object_name}/', view_func=view_func_rest, methods=['PATCH'])

        # delete : DELETE
        if 'D' in cruved:
            bp.add_url_rule(f'/{object_name}/', view_func=view_func_rest, methods=['DELELTE'])


