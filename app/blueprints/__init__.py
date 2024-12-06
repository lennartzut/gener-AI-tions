from .web.auth import web_auth_bp
from .web.individuals import web_individuals_bp
from .web.family_card import web_family_card_bp
from .web.identities import web_identities_bp
from .web.main import web_main_bp
from .web.profile import web_profile_bp

from .api.auth import api_auth_bp
from .api.individuals import api_individuals_bp
from .api.families import api_families_bp

__all__ = [
    'web_auth_bp',
    'web_individuals_bp',
    'web_main_bp',
    'web_profile_bp',
    'web_family_card_bp',
    'web_identities_bp',
    'api_auth_bp',
    'api_individuals_bp',
    'api_families_bp',
]
