
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

schemas = {
    'test' : [
        'parent',
        'child',
        'example'
    ],
    'utils': [
        'nomenclature',
        'nomenclature_type',
        'taxref',
        'organisme',
        'utilisateur',
        'synthese'
    ]
}

#insert routes
try:
    for group_name, object_names in schemas.items():
        for object_name in object_names:
            SchemaMethods(group_name, object_name).register_api(blueprint)

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
    
# @blueprint.route('/test', methods=['GET', 'POST'])
# def api_test():
#     return 'It works (ça marche !)'

