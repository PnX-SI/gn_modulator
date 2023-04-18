import sys
from flask import Blueprint, request, g, current_app
from .commands import commands
from .schema import SchemaMethods
from sqlalchemy.exc import NoForeignKeysError
from gn_modulator.module import ModuleMethods
from gn_modulator.layout import LayoutMethods
from gn_modulator import init_gn_modulator
from gn_modulator.utils.api import process_dict_path
from gn_modulator.utils.errors import get_errors, errors_txt
from gn_modulator import MODULE_CODE
from geonature.core.gn_permissions.decorators import check_cruved_scope
from geonature.core.gn_commons.models.base import TModules

blueprint = Blueprint(MODULE_CODE.lower(), __name__)

from gn_modulator.routes.rest import *  # noqa
from gn_modulator.routes.exports import *  # noqa
from gn_modulator.routes.imports import *  # noqa

# Creation des commandes pour modules
blueprint.cli.short_help = "Commandes pour l' administration du module MODULES"
for cmd in commands:
    blueprint.cli.add_command(cmd)


@blueprint.url_value_preprocessor
def set_current_module(endpoint, values):
    requested_module = values.get("module_code") or MODULE_CODE

    g.current_module = TModules.query.filter_by(module_code=requested_module).first_or_404(
        f"No module name {requested_module} {endpoint}"
    )


# On teste sys.argv pour éviter de charger les définitions
# si on est dans le cadre d'une commande
# On initialise dans le cadre d'une application lancée avec
# - gunicorn
# - celery
# - pytest
# - flask run
# - geonature run
test_init = any(sys.argv[0].endswith(x) for x in ["gunicorn", "celery", "pytest"]) or (
    len(sys.argv) >= 2 and sys.argv[1] == "run"
)

if test_init:
    init_gn_modulator()
    if get_errors():
        print(f"\n{errors_txt()}")


@blueprint.route("/config/<path:config_path>", methods=["GET"])
@blueprint.route("/config/", methods=["GET"], defaults={"config_path": None})
def api_modules_config(config_path):
    """
    renvoie la config des modules avec l'information sur le cruved des modules
    process_dict_path permet un aide à la navigation
    pour pouvoir explorer le dictionnaire de config à travers l'api
    """

    errors_init_module = get_errors()

    # s'il y a des erreurs à l'initialisation du module => on le fait remonter
    if len(errors_init_module) > 0:
        return f"Il y a {len(errors_init_module)} erreur(s) dans les définitions.", 500

    return process_dict_path(
        ModuleMethods.modules_config(),
        config_path,
        SchemaMethods.base_url() + "/config/",
    )


@check_cruved_scope("R")
@blueprint.route("breadcrumbs/<module_code>/<page_code>", methods=["GET"])
def api_breadcrumbs(module_code, page_code):
    """
    renvoie une liste de lien pour
    la page <page_code>
    du module <module_code>

    des arguments (id ou autres) peuvent être nécessaire pour
    accéder aux valeurs de l'object concerné par la page
    """

    return ModuleMethods.breadcrumbs(module_code, page_code, request.args.to_dict())


@blueprint.route("/layouts/<path:config_path>", methods=["GET"])
@blueprint.route("/layouts/", methods=["GET"], defaults={"config_path": None})
def api_layout(config_path):
    """
    Renvoie la liste des layouts
    """

    # paramètres

    # - as dict
    #   renvoie sous forme de dictonnaire avec les layout_code en clé
    #   destiné à la config
    as_dict = request.args.get("as_dict")
    # - filtre sur le nom des layouts
    layout_search_code = request.args.get("layout_search_code")
    # - pour un layout précis
    layout_code = request.args.get("layout_code")

    layout_out = None
    if layout_code:
        layout_out = LayoutMethods.get_layout(layout_code=layout_code)
    else:
        layout_out = LayoutMethods.get_layouts(
            layout_search_code=layout_search_code, as_dict=as_dict
        )

    return process_dict_path(
        layout_out,
        config_path,
        SchemaMethods.base_url() + "/layouts/",
    )


@blueprint.route("/schemas/<path:config_path>", methods=["GET"])
@blueprint.route("/schemas/", methods=["GET"], defaults={"config_path": None})
def api_schemas(config_path):
    """
    renvoie tous les schémas
    """

    schemas = {
        schema_code: {
            "properties": SchemaMethods(schema_code).properties_config(),
            "required": SchemaMethods(schema_code).attr("required"),
        }
        for schema_code in SchemaMethods.schema_codes()
    }

    return process_dict_path(
        schemas,
        config_path,
        SchemaMethods.base_url() + "/schemas/",
    )
