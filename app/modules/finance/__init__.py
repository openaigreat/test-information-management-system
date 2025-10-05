from flask import Blueprint

bp = Blueprint('finance', __name__)

from app.modules.finance import routes