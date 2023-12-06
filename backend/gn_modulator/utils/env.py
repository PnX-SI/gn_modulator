from geonature.utils.env import db, BACKEND_DIR
from flask import current_app
from ref_geo.utils import get_local_srid
from .cache import get_global_cache, set_global_cache
from pathlib import Path
import gn_modulator

gn_modulator_DIR = Path(gn_modulator.__file__).parent
migrations_directory = gn_modulator_DIR / "migrations"


config_modulator_dir = Path(__file__).parent / "../../../config"
definitions_test_dir = Path(__file__).parent / "../tests/definitions_test"
import_test_dir = Path(__file__).parent / "../tests/import_test"

schema_import = "gn_modulator_import"


def config_dir():
    return BACKEND_DIR / current_app.config["MEDIA_FOLDER"] / "modulator" / "config"


def assets_dir():
    return BACKEND_DIR / current_app.config["MEDIA_FOLDER"] / "modulator" / "assets"


def import_dir():
    return BACKEND_DIR / current_app.config["MEDIA_FOLDER"] / "modulator" / "imports"


def local_srid():
    """
    renvoie le local_srid depuis le cache
    (pour ne le demander qu'une seule fois à la base)
    """

    local_srid_ = get_global_cache(["local_srid"])

    if not local_srid_:
        local_srid_ = get_local_srid(db.session)
        set_global_cache(["local_srid"], local_srid_)

    return local_srid_
