from flask import redirect, url_for
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

from app.models.base_model import Base
from app.config import get_config

jwt = JWTManager()
cors = CORS()

engine = None
SessionLocal = scoped_session(sessionmaker())


def initialize_extensions(app):
    """
    Initialize and configure all extensions:
    - SQLAlchemy (engine, session)
    - Flask-JWT-Extended
    - Flask-CORS
    """
    global engine, SessionLocal

    app.logger.debug("Initializing SQLAlchemy extensions...")

    # Create the SQLAlchemy engine
    engine = create_engine(
        app.config["SQLALCHEMY_DATABASE_URI"],
        echo=app.config.get("SQLALCHEMY_ECHO", False),
        pool_size=int(app.config.get("SQLALCHEMY_POOL_SIZE", 5)),
        max_overflow=int(app.config.get("SQLALCHEMY_MAX_OVERFLOW", 10)),
    )
    app.logger.debug(f"Database engine created: {engine}")

    SessionLocal.configure(bind=engine)
    app.extensions["engine"] = engine

    # Initialize JWT
    jwt.init_app(app)

    # Initialize CORS
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("CORS_ALLOWED_ORIGINS", "*")}})

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_data):
        app.logger.warning("Token expired; redirecting to login.")
        return redirect(url_for("web_auth_bp.login"))

    app.logger.debug("All extensions initialized.")