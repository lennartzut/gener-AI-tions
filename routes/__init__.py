from flask import Blueprint
from .individuals import individuals_bp

# Main API Blueprint
api = Blueprint('api', __name__)

# Register Blueprints
api.register_blueprint(individuals_bp, url_prefix='/api/individuals')
