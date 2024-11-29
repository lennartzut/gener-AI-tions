from flask import Blueprint
from .auth import web_auth_bp
from .individuals import web_individuals_bp
from .main import web_main_bp
from .profile import web_profile_bp

web_bp = Blueprint('web_bp', __name__)

# Register Web blueprints under the main Web blueprint
web_bp.register_blueprint(web_auth_bp, url_prefix='/auth')
web_bp.register_blueprint(web_individuals_bp, url_prefix='/individuals')
web_bp.register_blueprint(web_main_bp)
web_bp.register_blueprint(web_profile_bp, url_prefix='/profile')

__all__ = ['web_bp', 'web_auth_bp', 'web_individuals_bp', 'web_main_bp', 'web_profile_bp']
