
from flask import Blueprint, request, jsonify, g
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

#insert routes
try:
    for schema_name in SchemaMethods.schema_names('schemas'):
        SchemaMethods(schema_name).register_api(blueprint)

except Exception as e:
    print('Erreur durant la création des routes pour {} : {}'.format(schema_name, str(e)))
    raise(e)

from geonature.core.gn_permissions.tools import (
    cruved_scope_for_user_in_module,
    get_user_permissions,
    get_user_from_token_and_raise,
    UserCruved,
)


@blueprint.route('/groups', methods=['GET'])
def api_groups():
    '''
        renvoi les groupes de schemas
    '''

    schema_names = SchemaMethods.schema_names('schemas')

    groups = {}

    for schema_name in schema_names:

        group_name = schema_name.split('.')[-2]
        object_name = schema_name.split('.')[-1]

        groups[group_name] = groups.get(group_name) or []
        groups[group_name].append(object_name)

    return groups


@blueprint.route('/modules_config', methods=['GET'])
def api_modules():

    module_schema = SchemaMethods('schemas.module.sous_module')

    query, _ = module_schema.get_list({})

    modules_dict = module_schema.serialize_list(query.all())

    for module in modules_dict:
        module_defs = SchemaMethods.load_json_file_from_name(module['module_name'])
        for key in module_defs:
            if key not in module:
                module[key] = module_defs[key]

        module['cruved'] = cruved_scope_for_user_in_module(g.current_user.id_role, module_code=module['module_code'])[0]


    return jsonify(modules_dict)

    module_names = SchemaMethods.schema_names('modules')

    modules = {}

    for module_name in module_names:
        modules[module_name] = SchemaMethods.load_json_file_from_name(module_name)


        modules[module_name]['cruved'] = cruved[0]

    return modules
