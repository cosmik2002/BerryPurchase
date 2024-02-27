from flask import Blueprint

bp = Blueprint('reports', __name__)

from app.reportsBp import routes
