import os
import logging
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate
from routes import api


def create_app():
    # Load environment variables
    load_dotenv()
    # Initialize Flask application
    app = Flask(__name__)
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in .env file.")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # Register blueprints
    app.register_blueprint(api)

    @app.route('/')
    def home():
        return {
            "message": "Welcome to Gener-AI-tions!",
            "status": "Running"
        }

    return app


# Run application
if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
