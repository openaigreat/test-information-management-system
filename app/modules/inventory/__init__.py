from flask import Blueprint

bp = Blueprint('inventory', __name__)

from app.modules.inventory import routes