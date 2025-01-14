from flask import Blueprint
from flask_swagger_ui import get_swaggerui_blueprint

swagger_bp = Blueprint('swagger_bp', __name__)

SWAGGER_URL = '/api/docs'
API_JSON_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_JSON_URL,
    config={
        'app_name': "Gener-AI-tions API"
    }
)

swagger_bp.register_blueprint(swaggerui_blueprint)
