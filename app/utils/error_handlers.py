from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError
from pydantic import ValidationError
from werkzeug.exceptions import (
    HTTPException,
    BadRequest,
    NotFound,
    Conflict,
    InternalServerError
)
from app.utils.response_helpers import error_response


def register_error_handlers(app):
    """
    Registers error handlers for the Flask application.
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        app.logger.error(f"Pydantic Validation Error: {e}")
        errors = []
        for err in e.errors():
            errors.append({
                'type': err['type'],
                'loc': err['loc'],
                'msg': err['msg']
            })
        return error_response({"validation_error": errors},
                              status_code=400)

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        app.logger.error(f"BadRequest: {e}")
        return error_response(str(e), 400)

    @app.errorhandler(NotFound)
    def handle_not_found(e):
        app.logger.error(f"NotFound: {e}")
        return error_response(str(e), 404)

    @app.errorhandler(Conflict)
    def handle_conflict(e):
        app.logger.warning(f"Conflict: {e}")
        return error_response(str(e), 409)

    @app.errorhandler(InternalServerError)
    def handle_internal_server_error(e):
        app.logger.error(f"InternalServerError: {e}")
        return error_response("An internal error occurred.", 500)

    @app.errorhandler(NoAuthorizationError)
    def handle_jwt_error(e):
        app.logger.warning(f"JWT Authorization Error: {e}")
        return error_response("Authorization required.", 401)

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_signature(e):
        app.logger.warning(f"Token expired: {e}")
        return error_response(
            "Token has expired. Please log in again.", 401)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        app.logger.error(f"HTTP Exception: {e}")
        return error_response(str(e), e.code)

    @app.errorhandler(Exception)
    def handle_general_exception(e):
        app.logger.error(f"Unhandled Exception: {type(e)}: {e}",
                         exc_info=True)
        return error_response("An unexpected error occurred.", 500)
