from flask import Blueprint
from .individuals import individuals_api_bp
from .families import families_api_bp
from .auth import auth_api_bp

api_bp = Blueprint('api', __name__)

# Register API blueprints
api_bp.register_blueprint(individuals_api_bp, url_prefix='/individuals')
api_bp.register_blueprint(families_api_bp, url_prefix='/families')
api_bp.register_blueprint(auth_api_bp, url_prefix='/auth')
