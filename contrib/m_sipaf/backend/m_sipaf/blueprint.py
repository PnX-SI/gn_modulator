from flask import Blueprint
from m_sipaf import MODULE_CODE

blueprint = Blueprint(MODULE_CODE.lower(), __name__)
