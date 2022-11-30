from flask import Blueprint, request, jsonify
from .commands import commands
from .schema import SchemaMethods
from sqlalchemy.exc import NoForeignKeysError
from gn_modules.module import ModuleMethods
from gn_modules.layout import LayoutMethods
from gn_modules import init_gn_modules
from gn_modules.utils.api import process_dict_path
from gn_modules.utils.errors import get_errors, errors_txt

blueprint = Blueprint("modules", __name__)

# Creation des commandes pour modules
blueprint.cli.short_help = "Commandes pour l' administration du module MODULES"
for cmd in commands:
    blueprint.cli.add_command(cmd)


# initialisation du module
try:
    init_gn_modules()
    if get_errors():
        print(f"\n{errors_txt()}")

except Exception as e:
    # patch 1ère initialisation flask run
    # sqlalchemy.exc.NoForeignKeysError:
    #   Could not determine join condition between parent/child tables on relationship TM_SipafPf.areas - there are no foreign keys linking these tables via secondary table 'm_sipaf.cor_area_pf'.  Ensure that referencing columns are associated with a ForeignKey or ForeignKeyConstraint, or specify 'primaryjoin' and 'secondaryjoin' expressions.
    if isinstance(e, NoForeignKeysError):
        pass
    raise e


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
        ModuleMethods.modules_config_with_cruved(),
        config_path,
        SchemaMethods.base_url() + "/config/",
    )


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


@blueprint.route("/layouts/", methods=["GET"])
def api_layout():
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

    if layout_code:
        return LayoutMethods.get_layout(layout_code=layout_code)

    return jsonify(
        LayoutMethods.get_layouts(layout_search_code=layout_search_code, as_dict=as_dict)
    )
