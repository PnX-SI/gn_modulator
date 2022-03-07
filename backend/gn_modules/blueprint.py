
from flask import Blueprint, request, jsonify, g, current_app
from gn_modules.module import ModuleMethods
from .commands import commands
from .schema import SchemaMethods, errors

blueprint = Blueprint('modules', __name__)

blueprint.cli.short_help = 'Commandes pour l''administration du module MODULES'
for cmd in commands:
    blueprint.cli.add_command(cmd)


try:
    SchemaMethods.init_schemas()
    SchemaMethods.init_routes(blueprint)

except errors.SchemaError as e:
    print("Erreur de chargement des schemas: {}".format(e))

# !!! attention restreindre les droits !!!

@blueprint.route('/modules_config', methods=['GET'])
def api_modules_config():

    return jsonify(ModuleMethods.modules_config())
