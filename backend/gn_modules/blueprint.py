from flask import Blueprint, request
from .commands import commands
from .schema import SchemaMethods
from sqlalchemy.exc import NoForeignKeysError
from gn_modules.module import ModuleMethods
from gn_modules.layout import LayoutMethods
from gn_modules import init_gn_modules
from gn_modules.utils.api import process_dict_path

blueprint = Blueprint("modules", __name__)

# Creation des commandes pour modules
blueprint.cli.short_help = "Commandes pour l' administration du module MODULES"
for cmd in commands:
    blueprint.cli.add_command(cmd)

errors_init_module = []

# initialisation du module
try:
    errors_init_module = init_gn_modules()
except Exception as e:
    # patch 1ère initialisation flask run
    # sqlalchemy.exc.NoForeignKeysError:
    #   Could not determine join condition between parent/child tables on relationship TM_SipafPf.areas - there are no foreign keys linking these tables via secondary table 'm_sipaf.cor_area_pf'.  Ensure that referencing columns are associated with a ForeignKey or ForeignKeyConstraint, or specify 'primaryjoin' and 'secondaryjoin' expressions.
    if isinstance(e, NoForeignKeysError):
        pass
    raise e


@blueprint.route("/modules_config/<path:config_path>", methods=["GET"])
@blueprint.route("/modules_config/", methods=["GET"], defaults={"config_path": None})
def api_modules_config(config_path):
    """
    renvoie la config des modules avec l'information sur le cruved des modules
    process_dict_path permet un aide à la navigation
    pour pouvoir explorer le dictionnaire de config à travers l'api
    """

    # s'il y a des erreurs à l'initialisation du module => on le fait remonter
    if len(errors_init_module) > 0:
        return f"Il y a {len(errors_init_module)} erreur(s) dans les définitions.", 500

    return process_dict_path(
        ModuleMethods.modules_config_with_cruved(),
        config_path,
        SchemaMethods.base_url() + "/modules_config/",
    )


@blueprint.route("breadcrumbs/<module_code>/<page_name>", methods=["GET"])
def api_breadcrumbs(module_code, page_name):
    """
    renvoie une liste de lien pour
    la page <page_name>
    du module <module_code>

    des arguments (id ou autres) peuvent être nécessaire pour
    accéder aux valeurs de l'object concerné par la page
    """

    return ModuleMethods.breadcrumbs(module_code, page_name, request.args.to_dict())


@blueprint.route("/layouts/", methods=["GET"])
def api_layout():
    """
    Renvoie la liste des layouts
    """

    return LayoutMethods.get_layouts()
