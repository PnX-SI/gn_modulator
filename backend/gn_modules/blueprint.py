
from distutils.command.config import config
from email.policy import default
from flask import Blueprint, request, jsonify, g, current_app, Response
from gn_modules.module import ModuleMethods
from pyrsistent import v
from .commands import commands
from .schema import SchemaMethods, errors
from sqlalchemy.exc import (
    InvalidRequestError, NoForeignKeysError
)

blueprint = Blueprint('modules', __name__)

# Creation des commandes pour modules
blueprint.cli.short_help = 'Commandes pour l''administration du module MODULES'
for cmd in commands:
    blueprint.cli.add_command(cmd)

try:
    ModuleMethods.init_modules()
    SchemaMethods.init_schemas_models_and_serializers()
    print('init ok')
except Exception as e:
    print('Erreur initialisation', str(e))


# ModuleMethods.process_commons_api(blueprint)

# initialisation des définitions
# TODO clarifier init route, ouvrir seulement les routes necessaire
# ou bien les ouvrir en admin ??
# try:
    # print('init definitions')
    # SchemaMethods.init_schemas_definitions()
    # print('init models')
    # SchemaMethods.init_schemas_models_and_serializers()
    # print('end')

    # SchemaMethods.init_routes(blueprint)
    # ModuleMethods.modules_config()

# except errors.SchemaError as e:
#     print("Erreur de chargement des schemas:\n{}".format(e))
# except InvalidRequestError as e:
#     print(e)
# except NoForeignKeysError as e:
#     print(e)
# except Exception as e:
#     print(e)


# route qui renvoie la configuration des modules
# fait office d'initialisation ?
@blueprint.route('/modules_config/<path:config_path>', methods=['GET'])
@blueprint.route('/modules_config/', methods=['GET'], defaults={'config_path': None})
def api_modules_config(config_path):

    modules_config = ModuleMethods.modules_config_with_rigths()

    return ModuleMethods.process_dict_path(
        modules_config,
        config_path,
        SchemaMethods.base_url() + '/modules_config/'
    )

@blueprint.route('breadcrumbs/<module_code>/<page_name>', methods=['GET'])
def api_breadcrumbs(module_code, page_name):
    '''
        TODO breadcrumb
    '''

    return ModuleMethods.breadcrumbs(module_code, page_name, request.args.to_dict())

@blueprint.route('export/<module_code>/<export_code>')
def api_export(module_code, export_code):
    '''
        TODO proprer
    '''
    module_config = ModuleMethods.module_config(module_code)

    export = next(x for x in module_config['exports'] if x['export_code'] == export_code)

    sm = SchemaMethods(export['schema_name'])

    return sm.process_export(export)




@blueprint.route('/layouts/', methods=['GET'])
def api_layout():
    '''
        Renvoie la liste des layouts
    '''

    return jsonify(SchemaMethods.get_layouts(as_dict=True))
