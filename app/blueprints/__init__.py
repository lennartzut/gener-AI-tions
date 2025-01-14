from .api.admin import api_admin_bp
from .api.auth import api_auth_bp
from .api.identities import api_identities_bp
from .api.individuals import api_individuals_bp
from .api.projects import api_projects_bp
from .api.relationships import api_relationships_bp
from .api.swagger import swagger_bp, swaggerui_blueprint
from .api.users import api_users_bp

from .web.auth import web_auth_bp
from .web.identities import web_identities_bp
from .web.individuals import web_individuals_bp
from .web.main import web_main_bp
from .web.projects import web_projects_bp
from .web.users import web_users_bp


def register_blueprints(app):
    """
    Registers all blueprints with the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """
    # API routes
    app.register_blueprint(api_admin_bp, url_prefix='/api/admin')
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_identities_bp,
                           url_prefix='/api/identities')
    app.register_blueprint(api_individuals_bp,
                           url_prefix='/api/individuals')
    app.register_blueprint(api_users_bp, url_prefix='/api/users')
    app.register_blueprint(api_projects_bp,
                           url_prefix='/api/projects')
    app.register_blueprint(api_relationships_bp,
                           url_prefix='/api/relationships')

    # Web routes
    app.register_blueprint(web_auth_bp, url_prefix='/auth')
    app.register_blueprint(web_identities_bp,
                           url_prefix='/identities')
    app.register_blueprint(web_individuals_bp,
                           url_prefix='/individuals')
    app.register_blueprint(web_main_bp)
    app.register_blueprint(web_users_bp, url_prefix='/users')
    app.register_blueprint(web_projects_bp, url_prefix='/projects')

    # Swagger
    app.register_blueprint(swagger_bp)
   