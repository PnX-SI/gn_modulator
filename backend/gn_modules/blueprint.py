
from flask import Blueprint, request, jsonify, g, current_app, Response
from gn_modules.module import ModuleMethods
from pyrsistent import v
from .commands import commands
from .schema import SchemaMethods, errors
from utils_flask_sqla.generic import GenericTable
from geonature.utils.env import db
from utils_flask_sqla.generic import serializeQuery
from utils_flask_sqla.response import to_csv_resp
from geonature.core.gn_permissions.tools import (
    cruved_scope_for_user_in_module,
)
import copy


blueprint = Blueprint('modules', __name__)

# Creation des commandes pour modules
blueprint.cli.short_help = 'Commandes pour l''administration du module MODULES'
for cmd in commands:
    blueprint.cli.add_command(cmd)

# initialisation des définitions
try:
    SchemaMethods.init_schemas_definitions()
    SchemaMethods.init_schemas_models_and_serializers()
    SchemaMethods.init_routes(blueprint)

except errors.SchemaError as e:
    print("Erreur de chargement des schemas:\n{}".format(e))
except Exception as e:
    print(e)


# @current_app.before_first_request
# def init_schemas():
#     print("init schemas")
#     try:
#         SchemaMethods.init_schemas_models_and_serializers()
#         # !!! attention restreindre les droits !!!
#         # SchemaMethods.init_routes(blueprint)

#     except errors.SchemaError as e:
#         print("Erreur de chargement des schemas:\n{}".format(e))


@blueprint.route('/modules_config', methods=['GET'])
def api_modules_config():

    modules_config = copy.deepcopy(ModuleMethods.modules_config())

    # pour ne pas exposer module_dir_path
    for key, module_config in modules_config.items():
        module_config.pop('module_dir_path')

    if not hasattr(g, 'current_user'):
        return modules_config

    # on calcule le cruved ici pour ne pas interférer avec le cache
    for key, module_config in modules_config.items():
        module_config['module']['cruved'] = {
            k: int(v)
            for k, v in cruved_scope_for_user_in_module(
                g.current_user.id_role,
                module_code=module_config['module']['module_code']
            )[0].items()
        }



    return {
        'modules': modules_config,
        'layouts': SchemaMethods.get_layouts(as_dict=True)
    }

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

    return jsonify(SchemaMethods.get_layouts())
