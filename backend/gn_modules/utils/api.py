import copy
from flask import jsonify


def process_dict_path(d, dict_path, base_url):
    """
    return dict or dict part according to path
    process error if needed
    """

    if not dict_path:
        return d

    p_error = []
    out = copy.deepcopy(d)
    for p in dict_path.split("/"):
        if p:
            # gestion des indices des listes
            try:
                p = int(p)
            except Exception:
                pass
            try:
                out = out[p]
                p_error.append(p)
            except Exception:
                path_error = "/".join(p_error)
                txt_error = "La chemin demandé <b>{}/{}</b> n'est pas correct\n".format(
                    path_error, p
                )
                if type(out) is dict and out.keys():
                    txt_error += "<br><br>Vous pouvez choisir un chemin parmi :"
                    for key in sorted(list(out.keys())):
                        url_key = base_url + path_error + "/" + key
                        txt_error += '<br> - <a href="{}">{}{}</a>'.format(
                            url_key, path_error + "/" if path_error else "", key
                        )
                return txt_error, 500

    return jsonify(out)
