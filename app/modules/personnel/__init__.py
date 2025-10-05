from flask import Blueprint

bp = Blueprint('personnel', __name__)

from app.modules.personnel import routes