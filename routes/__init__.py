from flask import Blueprint
from routes.individuals import individuals_bp
from routes.auth import auth_bp

# Main API Blueprint
api = Blueprint('api', __name__)

# Register Blueprints with URL prefixes
api.register_blueprint(auth_bp, url_prefix='/auth')
api.register_blueprint(individuals_bp, url_prefix='/individuals')
