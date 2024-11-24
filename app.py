import logging
from flask import Flask, jsonify
from pydantic import ValidationError
from config import DevelopmentConfig
from extensions import db, migrate
from routes import api


def create_app(config_class=DevelopmentConfig):
    # Initialize Flask application
    app = Flask(__name__)
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    # Apply configuration
    app.config.from_object(config_class)
    # Check if DATABASE_URL is set
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        raise ValueError(
            "DATABASE_URL not found in environment variables.")
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')

    @app.route('/')
    def home():
        return jsonify({
            "message": "Welcome to Gener-AI-tions!",
            "status": "Running"
        }), 200

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({'error': e.errors()}), 400

    return app


# Run application
if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
