from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app.models.base import Base

# Instantiate Flask extensions
db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
migrate = Migrate()
cors = CORS()

# Global variables for direct SQLAlchemy usage without Flask
engine = None
SessionLocal = scoped_session(sessionmaker())


def initialize_extensions(app):
    """
    Initialize and configure Flask and SQLAlchemy-related extensions.
    Sets up the SQLAlchemy engine, session, JWT, migrate, and CORS.
    """
    global engine, SessionLocal

    app.logger.debug("Initializing Flask extensions...")

    # Create the SQLAlchemy engine manually to allow flexibility
    engine = create_engine(
        app.config["SQLALCHEMY_DATABASE_URI"],
        echo=app.config.get("SQLALCHEMY_ECHO", False),
    )
    app.logger.debug(f"Database engine created: {engine}")

    # Configure scoped_session
    SessionLocal.configure(bind=engine)
    app.extensions['engine'] = engine

    # Initialize Flask-SQLAlchemy, using the engine from above
    # Since db is a SQLAlchemy instance tied to app, db.init_app sets up the session
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize JWT
    jwt.init_app(app)

    # Initialize CORS
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ALLOWED_ORIGINS"]}})
    app.logger.debug("All extensions initialized.")
