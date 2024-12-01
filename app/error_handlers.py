from flask import jsonify, render_template
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError


def register_error_handlers(app):
    """
    Registers error handlers for the Flask application.
    """

    # Handle Pydantic Validation Errors
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        app.logger.error(f"Pydantic Validation Error: {e}")
        return jsonify({'error': e.errors()}), 400

    # Handle 404 Errors (Page Not Found)
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 Error: {e}")
        return render_template('errors/404.html'), 404

    # Handle 500 Errors (Internal Server Error)
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 Error: {e}")
        return render_template('errors/500.html'), 500

    # Handle JWT Authorization Errors
    @app.errorhandler(NoAuthorizationError)
    def handle_jwt_error(e):
        app.logger.warning(f"JWT Authorization Error: {e}")
        return jsonify({'error': 'Authorization required.'}), 401

    # Handle Other HTTP Exceptions
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        app.logger.error(f"HTTP Exception: {e}")
        return jsonify({'error': e.description}), e.code

    # Handle Non-HTTP Exceptions (General Exceptions)
    @app.errorhandler(Exception)
    def handle_general_exception(e):
        app.logger.error(f"Unhandled Exception: {e}")
        return jsonify(
            {'error': 'An unexpected error occurred.'}), 500
