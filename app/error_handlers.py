from flask import jsonify, render_template, redirect, url_for, current_app
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError
from jwt import ExpiredSignatureError


def register_error_handlers(app):
    """
    Registers error handlers for the Flask application.
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        app.logger.error(f"Pydantic Validation Error: {e}")
        return jsonify({'error': e.errors()}), 400

    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 Error: {e}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 Error: {e}")
        return render_template('errors/500.html'), 500

    @app.errorhandler(NoAuthorizationError)
    def handle_jwt_error(e):
        app.logger.warning(f"JWT Authorization Error: {e}")
        return jsonify({'error': 'Authorization required.'}), 401

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_signature(e):
        current_app.logger.warning(f"Token expired: {e}")
        return redirect(url_for('web_auth_bp.login'))

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        app.logger.error(f"HTTP Exception: {e}")
        return jsonify({'error': e.description}), e.code

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        app.logger.error(f"Unhandled Exception: {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500