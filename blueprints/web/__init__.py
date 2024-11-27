from flask import Blueprint
from .main import main_web_bp
from .individuals import individuals_web_bp
from .profile import profile_web_bp

web_bp = Blueprint('web', __name__)

# Register web blueprints
web_bp.register_blueprint(main_web_bp)
web_bp.register_blueprint(individuals_web_bp, url_prefix='/individuals')
web_bp.register_blueprint(profile_web_bp, url_prefix='/profile')
