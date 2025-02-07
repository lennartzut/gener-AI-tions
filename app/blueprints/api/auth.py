import logging

from flask import Blueprint, request, current_app, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    unset_jwt_cookies,
    get_jwt_identity
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, Conflict, \
    InternalServerError

from app.extensions import SessionLocal
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.user_service import UserService, \
    UserAlreadyExistsError
from app.utils.response_helpers import success_response

logger = logging.getLogger(__name__)

api_auth_bp = Blueprint('api_auth_bp', __name__)


@api_auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user.
    Expects a JSON payload with 'username', 'email', 'password' and 'confirm_password'.
    Returns a JSON response with a success message or error details.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        user_create = UserCreate.model_validate(data)
    except Exception as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_user = UserService(db=session)
        try:
            new_user = service_user.create_user(
                user_create=user_create)
            if not new_user:
                raise Conflict("Email or username already in use.")
            return success_response(
                "Signup successful! Please log in.", status_code=201)
        except UserAlreadyExistsError as e:
            raise Conflict(str(e))
        except SQLAlchemyError as e:
            current_app.logger.error(f"Signup DB error: {e}")
            raise InternalServerError("Database error occurred.")


@api_auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate an existing user and issue JWT tokens.
    Expects a JSON payload with 'email' and 'password'.
    Returns a JSON response with a success message, sets JWT cookies or error details.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        user_login = UserLogin.model_validate(data)
    except Exception as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_user = UserService(db=session)
        try:
            user = service_user.authenticate_user(
                email=user_login.email, password=user_login.password)
            if user and user.id:
                access_token = create_access_token(
                    identity=str(user.id))
                refresh_token = create_refresh_token(
                    identity=str(user.id))
                response = jsonify({"message": "Login successful!"})
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                return response, 200
            raise BadRequest("Invalid email or password.")
        except SQLAlchemyError as e:
            current_app.logger.error(f"Login DB error: {e}")
            raise InternalServerError("Database error occurred.")


@api_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh the access token using a valid refresh token.
    Returns a JSON response with a new access token cookie or error details.
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            raise BadRequest("No user identity in token.")
        new_access_token = create_access_token(identity=user_id)
        response = jsonify(
            {"message": "Token refreshed successfully."})
        set_access_cookies(response, new_access_token)
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error refreshing token: {e}")
        raise InternalServerError("Token refresh failed.")


@api_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Log out the current user by unsetting JWT cookies.
    Returns a JSON response with a success message.
    """
    response = jsonify({"message": "Logged out successfully."})
    unset_jwt_cookies(response)
    return response, 200
