"""
This module initializes and configures Flask extensions for the application.

Extensions are initialized here to ensure they can be imported and used
across the application without circular import issues.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# Database extension
db = SQLAlchemy()

# Database migration extension
migrate = Migrate()

# JWT authentication manager
jwt = JWTManager()

# Bcrypt for password hashing
bcrypt = Bcrypt()
