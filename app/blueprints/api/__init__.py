from .auth import api_auth_bp
from .individuals import api_individuals_bp
from .families import api_families_bp
from .relationships import api_relationships_bp

__all__ = ['api_auth_bp', 'api_individuals_bp', 'api_families_bp',
           'api_relationships_bp']
