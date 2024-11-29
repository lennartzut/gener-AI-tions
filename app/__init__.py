import logging
from flask import Flask, jsonify, render_template
from flask_jwt_extended import get_jwt_identity
from pydantic import ValidationError
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
from app.extensions import db, migrate, jwt
from app.blueprints import (
    web_auth_bp,
    web_individuals_bp,
    web_main_bp,
    web_profile_bp,
    api_auth_bp,
    api_individuals_bp,
    api_families_bp
)
from app.models.user import User


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)

    # Configure Logging
    configure_logging()

    # Load Configuration
    app.config.from_object(config_class)
    validate_configuration(app)

    # Initialize Extensions
    initialize_extensions(app)

    # Register Blueprints
    register_blueprints(app)

    # Register Context Processors
    register_context_processors(app)

    # Register JWT Callbacks
    register_jwt_callbacks(app)

    # Register Error Handlers
    register_error_handlers(app)

    return app


def configure_logging():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)


def validate_configuration(app):
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.logger.error("DATABASE_URL not found in environment variables.")
        raise ValueError("DATABASE_URL not found in environment variables.")


def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


def register_blueprints(app):
    # Register web blueprints
    app.register_blueprint(web_auth_bp)
    app.register_blueprint(web_individuals_bp)
    app.register_blueprint(web_main_bp)
    app.register_blueprint(web_profile_bp)

    # Register API blueprints
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(api_individuals_bp)
    app.register_blueprint(api_families_bp)


def register_context_processors(app):
    @app.context_processor
    def inject_current_user():
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(int(user_id))  # Ensure user_id is integer
        except Exception as e:
            app.logger.warning(f"Failed to inject current user: {e}")
        return dict(current_user=user)


def register_jwt_callbacks(app):
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data.get("sub")
        try:
            user_id = int(identity)  # Ensure identity is an integer
            user = User.query.get(user_id)
            if not user:
                app.logger.warning(f"User with ID {user_id} not found.")
            return user
        except (ValueError, TypeError) as e:
            app.logger.error(f"Invalid JWT identity: {e}")
            return None


def register_error_handlers(app):
    # Handle Pydantic Validation Errors
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        app.logger.error(f"Pydantic Validation Error: {e}")
        return jsonify({'error': e.errors()}), 400

    # Handle 404 Errors
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 Error: {e}")
        return render_template('errors/404.html'), 404

    # Handle 500 Errors
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 Error: {e}")
        return render_template('errors/500.html'), 500
