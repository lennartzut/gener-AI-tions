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
    web_family_card_bp,
    web_identities_bp,
    api_auth_bp,
    api_individuals_bp,
    api_families_bp
)
from app.models.user import User
from app.context_processors import inject_current_user
from app.error_handlers import register_error_handlers


def create_app(config_class=DevelopmentConfig):
    """
    Application factory function to initialize and configure the Flask app.
    """
    app = Flask(__name__)

    # Load Configuration
    app.config.from_object(config_class)
    validate_configuration(app)

    # Initialize Components
    configure_logging()
    initialize_extensions(app)
    register_blueprints(app)
    app.context_processor(inject_current_user)
    register_jwt_callbacks(app)
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
    Validates required application configuration.
    """
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.logger.error(
            "SQLALCHEMY_DATABASE_URI not found in configuration.")
        raise ValueError("SQLALCHEMY_DATABASE_URI must be set.")


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
    # Web blueprints
    app.register_blueprint(web_auth_bp, url_prefix='/auth')
    app.register_blueprint(web_individuals_bp,
                           url_prefix='/individuals')
    app.register_blueprint(web_main_bp, url_prefix='/')
    app.register_blueprint(web_profile_bp, url_prefix='/profile')
    app.register_blueprint(web_identities_bp,
                           url_prefix='/identities')
    app.register_blueprint(web_family_card_bp,
                           url_prefix='/family-card')

    # API blueprints
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_individuals_bp,
                           url_prefix='/api/individuals')
    app.register_blueprint(api_families_bp,
                           url_prefix='/api/families')


def register_jwt_callbacks(app):
    """
    Registers JWT callbacks for user identity handling.
    """

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Loads the user based on the JWT identity.
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
