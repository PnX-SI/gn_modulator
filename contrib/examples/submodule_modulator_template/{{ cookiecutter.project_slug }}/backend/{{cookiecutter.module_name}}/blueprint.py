from flask import Blueprint
from {{cookiecutter.module_name}} import MODULE_CODE

blueprint = Blueprint(MODULE_CODE.lower(), __name__)
