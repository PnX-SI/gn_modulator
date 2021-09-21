
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

#insert route de test
try:
    sm = SchemaMethods('test', 'example')
    sm.register_api(blueprint)
except Exception as e:
    print('Erreur durant la création des routes test : {}'.format(str(e)))
    raise(e)

# TODO dans register api
@blueprint.route('/schema/<module_code>/<schema_name>', methods=['GET'])
def api_schema(module_code, schema_name):
    '''
        api schema
    '''
    try:
        sm = SchemaMethods(module_code, schema_name)
        return sm.schema()
    except Exception as e:
        return 'erreur {}'.format(e), 500
@blueprint.route('/test', methods=['GET', 'POST'])
def api_test():
    return 'It works (ça marche !)'

