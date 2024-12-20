from .api.auth import api_auth_bp
from .api.citations import api_citations_bp
from .api.custom_enums import api_custom_enums_bp
from .api.custom_fields import api_custom_fields_bp
from .api.events import api_events_bp
from .api.families import api_families_bp
from .api.identities import api_identities_bp
from .api.individuals import api_individuals_bp
from .api.profile import api_profile_bp
from .api.projects import api_projects_bp
from .api.relationships import api_relationships_bp

from .web.auth import web_auth_bp
from .web.citations import web_citations_bp
from .web.custom_enums import web_custom_enums_bp
from .web.custom_fields import web_custom_fields_bp
from .web.events import web_events_bp
from .web.families import web_families_bp
from .web.identities import web_identities_bp
from .web.individuals import web_individuals_bp
from .web.main import web_main_bp
from .web.profile import web_profile_bp
from .web.projects import web_projects_bp
from .web.sources import web_sources_bp

from .api.swagger import swagger_bp, swaggerui_blueprint

def register_blueprints(app):
    """
    Registers all blueprints with the Flask application.
    """
    # API blueprints
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_citations_bp,
                           url_prefix='/api/citations')
    app.register_blueprint(api_custom_enums_bp,
                           url_prefix='/api/custom_enums')
    app.register_blueprint(api_custom_fields_bp,
                           url_prefix='/api/custom_fields')
    app.register_blueprint(api_events_bp, url_prefix='/api/events')
    app.register_blueprint(api_families_bp, url_prefix='/api/families')
    app.register_blueprint(api_identities_bp, url_prefix='/api/identities')
    app.register_blueprint(api_individuals_bp, url_prefix='/api/individuals')
    app.register_blueprint(api_profile_bp, url_prefix='/api/profile')
    app.register_blueprint(api_projects_bp, url_prefix='/api/projects')
    app.register_blueprint(api_relationships_bp, url_prefix='/api/relationships')

    # Web blueprints
    app.register_blueprint(web_auth_bp, url_prefix='/auth')
    app.register_blueprint(web_citations_bp, url_prefix='/citations')
    app.register_blueprint(web_custom_enums_bp,
                           url_prefix='/custom_enums')
    app.register_blueprint(web_custom_fields_bp,
                           url_prefix='/custom_fields')
    app.register_blueprint(web_events_bp, url_prefix='/events')
    app.register_blueprint(web_families_bp, url_prefix='/families')
    app.register_blueprint(web_identities_bp, url_prefix='/identities')
    app.register_blueprint(web_individuals_bp, url_prefix='/individuals')
    app.register_blueprint(web_main_bp)
    app.register_blueprint(web_profile_bp, url_prefix='/profile')
    app.register_blueprint(web_projects_bp, url_prefix='/projects')
    app.register_blueprint(web_sources_bp, url_prefix='/sources')

    app.register_blueprint(swagger_bp)





