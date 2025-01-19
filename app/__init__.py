import logging

from flask import Flask

from app.blueprints import register_blueprints
from app.config import get_config
from app.utils.context_processors import inject_current_user
from app.utils.error_handlers import register_error_handlers
from app.extensions import initialize_extensions


def create_app(env: str = "development"):
    """
    Application factory for creating and configuring the Flask
    app instance.

    Args:
        env (str): The environment to configure the app for.
        Defaults to "development".

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    app.config.from_object(get_config(env))
    validate_configuration(app)

    configure_logging(app)

    initialize_extensions(app)

    app.context_processor(inject_current_user)
    register_blueprints(app)
    register_error_handlers(app)

    @app.route("/health", methods=["GET"])
    def health():
        """
        Health check endpoint to verify the application's status.

        Returns:
            tuple: JSON response with status and HTTP status code 200.
        """
        return {"status": "healthy"}, 200

    return app


def configure_logging(app):
    """
    Configures logging for the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug("Logging configured with DEBUG level.")


def validate_configuration(app):
    """
    Validates required application configuration.

    Ensures that essential configuration variables are set.
    Raises:
        ValueError: If any required configuration is missing or
        invalid.
    Args:
        app (Flask): The Flask application instance.
    """
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.logger.error(
            "SQLALCHEMY_DATABASE_URI not found in configuration.")
        raise ValueError("SQLALCHEMY_DATABASE_URI must be set.")
