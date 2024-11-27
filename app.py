import logging
from flask import Flask, jsonify, render_template
from flask_jwt_extended import get_jwt_identity
from pydantic import ValidationError
from config import DevelopmentConfig
from extensions import db, migrate, jwt
from blueprints import auth_bp, api_bp, web_bp
from models.user import User


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    logging.basicConfig(level=logging.DEBUG)
    app.config.from_object(config_class)

    if not app.config['SQLALCHEMY_DATABASE_URI']:
        raise ValueError("DATABASE_URL not found in environment variables.")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)

    @app.context_processor
    def inject_current_user():
        user = None
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
        except:
            # No JWT present or invalid token
            pass
        return dict(current_user=user)

    # User lookup callback for JWT
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        try:
            user_id = int(
                identity)  # Convert the identity back to an integer
        except (ValueError, TypeError):
            # Handle the error, possibly by returning None
            return None
        return User.query.get(user_id)

    # Error handler for Pydantic validation errors
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({'error': e.errors()}), 400

    # 404 Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    # 500 Internal Server Error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500


    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
