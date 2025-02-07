from functools import lru_cache

from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
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

    Args:
        app (Flask): The Flask application instance.
    """
    global engine, SessionLocal

    engine = create_engine(
        app.config["SQLALCHEMY_DATABASE_URI"],
        echo=app.config.get("SQLALCHEMY_ECHO", False),
        pool_size=app.config.get("SQLALCHEMY_POOL_SIZE", 5),
        max_overflow=app.config.get("SQLALCHEMY_MAX_OVERFLOW", 10),
    )
    app.logger.debug(f"Database engine created: {engine}")

    SessionLocal.configure(bind=engine)
    app.extensions["engine"] = engine

    jwt.init_app(app)

    cors.init_app(app, resources={r"/*": {
        "origins": app.config.get("CORS_ALLOWED_ORIGINS", "*")}})

    @jwt.expired_token_loader
    def handle_expired_token(_jwt_header, _jwt_data):
        """
        Handles expired JWT tokens by returning a JSON response.
        """
        app.logger.warning(
            "Token expired. Returning 401 Unauthorized.")
        return jsonify(
            {"error": "Token expired. Please log in again."}), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(error):
        """
        Handles invalid JWT tokens by returning a JSON response.
        """
        app.logger.warning(f"Invalid token. Error: {error}")
        return jsonify(
            {"error": "Invalid token. Please log in again."}), 401

    @jwt.unauthorized_loader
    def handle_missing_token(error):
        """
        Handles missing JWT tokens by returning a JSON response.
        """
        app.logger.warning(f"Missing token. Error: {error}")
        return jsonify(
            {"error": "Authorization token required."}), 401

    @jwt.revoked_token_loader
    def handle_revoked_token(_jwt_header, _jwt_data):
        """
        Handles revoked JWT tokens by returning a JSON response.
        """
        app.logger.warning("Token has been revoked.")
        return jsonify(
            {"error": "Token revoked. Please log in again."}), 401

    @lru_cache(maxsize=1024)
    def get_user_admin_status(user_id: int) -> bool:
        """
        Retrieve the admin status for a user from the database.
        This function is cached to avoid repeated DB queries for the same user.
        """
        try:
            with SessionLocal() as session:
                user = session.query(User).filter(
                    User.id == user_id).first()
                if user:
                    return user.is_admin
        except Exception as e:
            app.logger.error(
                f"Error retrieving admin status for user {user_id}: {e}")
        return False

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        """
        Adds additional claims to the JWT, such as admin status.
        Uses a cached lookup to minimize performance overhead.
        Args:
            identity (str): The identity of the user (usually user ID).
        Returns:
            dict: Additional JWT claims.
        """
        try:
            user_id = int(identity)
            is_admin = get_user_admin_status(user_id)
            return {"is_admin": is_admin}
        except Exception as e:
            app.logger.error(f"Error adding claims to JWT: {e}")
        return {"is_admin": False}

    app.logger.debug("All extensions initialized.")
