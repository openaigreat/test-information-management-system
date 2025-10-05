from flask import Blueprint

bp = Blueprint('knowledge', __name__)

from app.modules.knowledge import routes