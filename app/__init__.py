import logging
from flask import Flask
from app.config import get_config
from app.extensions import initialize_extensions, db, engine, SessionLocal
from app.blueprints import register_blueprints
from app.error_handlers import register_error_handlers
from app.context_processors import inject_current_user
from app.utils.bcrypt_util import bcrypt


def create_app(env: str = 'development'):
    """
    Application factory for creating and configuring the Flask app instance.
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(get_config(env))
    validate_configuration(app)

    # Configure logging
    configure_logging(app)

    # Initialize extensions (db, jwt, migrate, cors)
    initialize_extensions(app)
    bcrypt.init_app(app)

    # Register blueprints, context processors, and error handlers
    register_blueprints(app)
    app.context_processor(inject_current_user)
    register_error_handlers(app)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "healthy"}, 200

    return app


def configure_logging(app):
    """
    Configures logging for the Flask application.
    """
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug("Logging configured with DEBUG level.")


def validate_configuration(app):
    """
    Validates required application configuration.
    Raises ValueError if configuration is invalid.
    """
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.logger.error("SQLALCHEMY_DATABASE_URI not found in configuration.")
        raise ValueError("SQLALCHEMY_DATABASE_URI must be set.")
