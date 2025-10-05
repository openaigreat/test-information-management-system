from flask import Blueprint

bp = Blueprint('customers', __name__)

from app.modules.customers import routes