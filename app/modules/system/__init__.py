from flask import Blueprint

bp = Blueprint('system', __name__)

from app.modules.system import routes