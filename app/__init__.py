import logging
from flask import Flask
from app.config import DevelopmentConfig, TestingConfig, \
    ProductionConfig
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
from app.context_processors import inject_current_user
from app.error_handlers import register_error_handlers


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
    app.context_processor(inject_current_user)

    # Register JWT Callbacks
    register_jwt_callbacks(app)

    # Register Error Handlers
    register_error_handlers(app)

    return app


def configure_logging():
    """
    Configures logging for the Flask application.
    """
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)


def validate_configuration(app):
    """
    Validates the Flask application configuration.
    """
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.logger.error(
            "DATABASE_URL not found in environment variables.")
        raise ValueError(
            "DATABASE_URL not found in environment variables.")


def initialize_extensions(app):
    """
    Initializes Flask extensions.
    """
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


def register_blueprints(app):
    """
    Registers all blueprints with the Flask application.
    """
    # Register web blueprints
    app.register_blueprint(web_auth_bp, url_prefix='/auth')
    app.register_blueprint(web_individuals_bp,
                           url_prefix='/individuals')
    app.register_blueprint(web_main_bp)
    app.register_blueprint(web_profile_bp, url_prefix='/profile')

    # Register API blueprints
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_individuals_bp,
                           url_prefix='/api/individuals')
    app.register_blueprint(api_families_bp,
                           url_prefix='/api/families')


def register_jwt_callbacks(app):
    """
    Registers JWT callbacks for user lookup.
    """

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Callback to load the user from the database based on the JWT identity.
        """
        identity = jwt_data.get("sub")
        try:
            user_id = int(identity)
            user = User.query.get(user_id)
            if not user:
                app.logger.warning(
                    f"User with ID {user_id} not found.")
            return user
        except (ValueError, TypeError) as e:
            app.logger.error(f"Invalid JWT identity: {e}")
            return None
