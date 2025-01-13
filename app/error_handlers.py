from flask import jsonify, current_app
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

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        current_app.logger.error(
            f"ValueError captured in global handler: {e}")
        return jsonify({'error': str(e)}), 400

    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 Error: {e}")
        return jsonify({'error': 'Resource not found.'}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 Error: {e}")
        return jsonify(
            {'error': 'An internal server error occurred.'}), 500

    @app.errorhandler(NoAuthorizationError)
    def handle_jwt_error(e):
        app.logger.warning(f"JWT Authorization Error: {e}")
        return jsonify({'error': 'Authorization required.'}), 401

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_signature(e):
        current_app.logger.warning(f"Token expired: {e}")
        return jsonify({
            'error': 'Token has expired. Please log in again.'}), 401

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        app.logger.error(f"HTTP Exception: {e}")
        return jsonify({'error': e.description}), e.code

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        if isinstance(e, ValidationError):
            return handle_validation_error(e)
        if isinstance(e, ValueError):
            return handle_value_error(e)
        if hasattr(e, "__cause__") and isinstance(e.__cause__, ValueError):
            return handle_value_error(e.__cause__)
        current_app.logger.error(f"Unhandled Exception Type:"
                                 f" {type(e)} | Exception: {e}")
        return jsonify(
            {'error': 'An unexpected error occurred.'}), 500
