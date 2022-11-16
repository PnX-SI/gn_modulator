from geonature.utils.env import db, BACKEND_DIR
from ref_geo.utils import get_local_srid
from .cache import get_global_cache, set_global_cache

import os
from pathlib import Path
import gn_modules

GN_MODULES_DIR = Path(gn_modules.__file__).parent


assets_static_dir = BACKEND_DIR / "static/external_assets/modules/"
config_directory = GN_MODULES_DIR / "../../config/"
migrations_directory = GN_MODULES_DIR / "backend/gn_modules/migrations"


def local_srid():
    """
    renvoie le local_srid depuis le cache
    (pour ne le demander qu'une seule fois à la base)
    """

    local_srid_ = get_global_cache(["local_srid"])

    if not local_srid_:
        local_srid_ = get_local_srid(db.engine)
        set_global_cache(["local_srid"], local_srid_)

    return local_srid_
