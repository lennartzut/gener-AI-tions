from flask import Blueprint
from flask_swagger_ui import get_swaggerui_blueprint

swagger_bp = Blueprint('swagger_bp', __name__)

# Define the URL for the Swagger UI and the path to the Swagger JSON
SWAGGER_URL = '/api/docs'  # URL to access Swagger UI
API_JSON_URL = '/static/swagger.json'  # Path to the Swagger JSON file

# Set up the Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_JSON_URL,
    config={
        'app_name': "Gener-AI-tions API"
    }
)

# Register the Swagger UI blueprint
swagger_bp.register_blueprint(swaggerui_blueprint)
