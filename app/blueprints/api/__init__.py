from flask import Blueprint
from .auth import api_auth_bp
from .individuals import api_individuals_bp
from .families import api_families_bp

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

# Register API blueprints under the main API blueprint
api_bp.register_blueprint(api_auth_bp, url_prefix='/auth')
api_bp.register_blueprint(api_individuals_bp, url_prefix='/individuals')
api_bp.register_blueprint(api_families_bp, url_prefix='/families')

__all__ = ['api_bp', 'api_auth_bp', 'api_individuals_bp', 'api_families_bp']
