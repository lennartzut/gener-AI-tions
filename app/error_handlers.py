from flask import jsonify, current_app
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """
    Registers error handlers for the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """
        Handles Pydantic validation errors.

        Args:
            e (ValidationError): The exception instance.

        Returns:
            tuple: JSON response with error details and HTTP
            status code 400.
        """
        app.logger.error(f"Pydantic Validation Error: {e}")
        errors = [
            {
                'type': error['type'],
                'loc': error['loc'],
                'msg': error['msg']
            }
            for error in e.errors()
        ]
        return jsonify(
            {'error': 'Validation failed.', 'details': errors}), 400

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        """
        Handles ValueError exceptions, typically related to
        business logic errors.

        Args:
            e (ValueError): The exception instance.

        Returns:
            tuple: JSON response with error message and HTTP
            status code 400.
        """
        current_app.logger.error(f"ValueError captured: {e}")
        return jsonify({'error': str(e)}), 400

    @app.errorhandler(NoAuthorizationError)
    def handle_jwt_error(e):
        """
        Handles JWT authorization errors.

        Args:
            e (NoAuthorizationError): The exception instance.

        Returns:
            tuple: JSON response indicating authorization is
            required with HTTP status code 401.
        """
        app.logger.warning(f"JWT Authorization Error: {e}")
        return jsonify({'error': 'Authorization required.'}), 401

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_signature(e):
        """
        Handles expired JWT tokens.

        Args:
            e (ExpiredSignatureError): The exception instance.

        Returns:
            tuple: JSON response indicating token expiration with
            HTTP status code 401.
        """
        current_app.logger.warning(f"Token expired: {e}")
        return jsonify({
            'error': 'Token has expired. Please log in again.'}), 401

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """
        Handles HTTP exceptions such as 404 Not Found.

        Args:
            e (HTTPException): The exception instance.

        Returns:
            tuple: JSON response with error description and
            corresponding HTTP status code.
        """
        app.logger.error(f"HTTP Exception: {e}")
        return jsonify({'error': e.description}), e.code

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        """
        Handles all unhandled exceptions, ensuring they are logged
        and a generic error is returned.

        Args:
            e (Exception): The exception instance.

        Returns:
            tuple: JSON response indicating an unexpected error
            with HTTP status code 500.
        """
        if isinstance(e, ValidationError):
            return handle_validation_error(e)
        if isinstance(e, ValueError):
            return handle_value_error(e)
        if hasattr(e, "__cause__") and isinstance(e.__cause__,
                                                  ValueError):
            return handle_value_error(e.__cause__)

        app.logger.error(
            f"Unhandled Exception Type: {type(e)} | Exception: {e}",
            exc_info=True)
        return jsonify(
            {'error': 'An unexpected error occurred.'}), 500
