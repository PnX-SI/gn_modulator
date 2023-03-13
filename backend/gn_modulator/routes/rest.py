from gn_modulator.blueprint import blueprint
from .utils.decorators import check_rest_route
from .utils.repository import (
    get_list_rest,
    get_one_rest,
    get_page_number_and_list,
    post_rest,
    patch_rest,
    delete_rest,
)


@blueprint.route("/rest/<module_code>/<object_code>/", methods=["GET"])
@check_rest_route("R")
def api_rest_get_list(module_code, object_code):
    """
    Route pour récupérer les listes
    """

    return get_list_rest(module_code, object_code)


@blueprint.route("/rest/<module_code>/<object_code>/<value>", methods=["GET"])
@check_rest_route("R")
def api_rest_get_one(module_code, object_code, value):
    """
    Route pour récupérer une ligne
    """

    return get_one_rest(module_code, object_code, value)


@blueprint.route("/page_number_and_list/<module_code>/<object_code>/<value>", methods=["GET"])
@check_rest_route("R")
def api_rest_get_page_number_and_list(module_code, object_code, value):
    """
    Route pour récupérer une liste à partir d'un ligne
    dont on va chercher le numero de page
    et renvoyer la liste de la page
    """

    return get_page_number_and_list(module_code, object_code, value)


@blueprint.route("/rest/<module_code>/<object_code>/", methods=["POST"])
@check_rest_route("C")
def api_rest_post(module_code, object_code):
    """
    Route pour créer une nouvelle ligne
    """

    return post_rest(module_code, object_code)


@blueprint.route("/rest/<module_code>/<object_code>/<value>", methods=["PATCH"])
@check_rest_route("U")
def api_rest_patch(module_code, object_code, value):
    """
    Route pour modifier une ligne
    """

    return patch_rest(module_code, object_code, value)


@blueprint.route("/rest/<module_code>/<object_code>/<value>", methods=["DELETE"])
@check_rest_route("D")
def api_rest_delete(module_code, object_code, value):
    """
    Route pour supprimer une ligne
    """

    return delete_rest(module_code, object_code, value)
