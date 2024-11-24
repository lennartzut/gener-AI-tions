from flask import Blueprint
from routes.individuals import individuals_bp

# Main API Blueprint
api = Blueprint('api', __name__)

# Register Blueprints with URL prefixes
api.register_blueprint(individuals_bp, url_prefix='/individuals')
