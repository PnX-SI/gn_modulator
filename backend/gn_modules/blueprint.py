
from flask import Blueprint, request, jsonify
from .commands import commands
from .schema import SchemaMethods
# from .utils.api import register_api
# from .utils.file import get_json_from_file
# from pathlib import Path
# from geonature.utils.env import (
#     DB,
#     GN_EXTERNAL_MODULE
# )
# from gn_modules import MODULE_CODE


blueprint = Blueprint('modules', __name__)

blueprint.cli.short_help = 'Commandes pour l''administration du module MODULES'
for cmd in commands:
    blueprint.cli.add_command(cmd)

schema_groups = [
    {
        'name': 'test',
        'label': "Test",
        'items': [
            'parent',
            'child',
            'example'
        ],
    },
    {
        'name': 'utils',
        'label': 'Utils',
        'items': [
            'nomenclature',
            'nomenclature_type',
            'taxref',
            'organisme',
            'utilisateur',
            'synthese'
        ],
    },
    {
        'name': 'sipaf',
        'label': 'Sipaf',
        'items': [ 'pf' ]
    }
]

#insert routes
try:
    for group in schema_groups:
        for object_name in group['items']:
            SchemaMethods(group['name'], object_name).register_api(blueprint)

except Exception as e:
    print('Erreur durant la création des routes test : {}'.format(str(e)))
    raise(e)

# TODO dans register api
# @blueprint.route('/schema/<group_name>/<object_name>', methods=['GET'])
# def api_schema(group_name, object_name):
#     '''
#         api schema
#     '''
#     try:
#         sm = SchemaMethods(group_name, object_name)
#         return sm.schema()
#     except Exception as e:
#         return 'erreur {}'.format(e), 500

@blueprint.route('/groups', methods=['GET'])
def api_groups():
    '''
        renvoi les groupes de schemas
    '''
    return jsonify(schema_groups)

