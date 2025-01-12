from flask import jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.models.user_model import User

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

    # Create the SQLAlchemy engine
    app.logger.debug("Initializing SQLAlchemy extensions...")
    engine = create_engine(
        app.config["SQLALCHEMY_DATABASE_URI"],
        echo=app.config.get("SQLALCHEMY_ECHO", False),
        pool_size=app.config.get("SQLALCHEMY_POOL_SIZE", 5),
        max_overflow=app.config.get("SQLALCHEMY_MAX_OVERFLOW", 10),
    )
    app.logger.debug(f"Database engine created: {engine}")

    SessionLocal.configure(bind=engine)
    app.extensions["engine"] = engine

    # Initialize JWT
    jwt.init_app(app)

    # Initialize CORS
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("CORS_ALLOWED_ORIGINS", "*")}})

    # Handle expired tokens with a JSON response
    @jwt.expired_token_loader
    def handle_expired_token(_jwt_header, _jwt_data):
        app.logger.warning("Token expired. Returning 401 Unauthorized.")
        return jsonify({"error": "Token expired. Please log in again."}), 401

    # Log invalid token claims
    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        app.logger.warning(f"Invalid token. Error: {error}")
        return jsonify({"error": "Invalid token. Please log in again."}), 401

    # Log missing token
    @jwt.unauthorized_loader
    def handle_missing_token(error):
        app.logger.warning(f"Missing token. Error: {error}")
        return jsonify({"error": "Authorization token required."}), 401

    # Log revoked tokens
    @jwt.revoked_token_loader
    def handle_revoked_token(_jwt_header, _jwt_data):
        app.logger.warning("Token has been revoked.")
        return jsonify({"error": "Token revoked. Please log in again."}), 401

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        """
        Adds extra claims to JWT.
        """
        try:
            user_id = int(identity)
            with SessionLocal() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    return {"is_admin": user.is_admin}
        except Exception as e:
            app.logger.error(f"Error adding claims to JWT: {e}")
        return {"is_admin": False}

    app.logger.debug("All extensions initialized.")
