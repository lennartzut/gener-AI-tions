from flask import Blueprint
from .core import core_bp
from .family import family_bp
from .identities import identities_bp

individuals_bp = Blueprint('individuals', __name__)

# Register sub-blueprints with URL prefixes
individuals_bp.register_blueprint(core_bp, url_prefix='/')
individuals_bp.register_blueprint(family_bp, url_prefix='/')
individuals_bp.register_blueprint(identities_bp, url_prefix='/')
