from .auth import web_auth_bp
from .individuals import web_individuals_bp
from .main import web_main_bp
from .profile import web_profile_bp
from .family_card import web_family_card_bp
from .identities import web_identities_bp

__all__ = ['web_auth_bp', 'web_individuals_bp', 'web_main_bp',
           'web_profile_bp', 'web_family_card_bp', 'web_identities_bp']
