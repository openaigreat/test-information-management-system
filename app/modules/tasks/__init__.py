from flask import Blueprint

bp = Blueprint('tasks', __name__)

from app.modules.tasks import routes