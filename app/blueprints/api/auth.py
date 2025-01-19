from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    jwt_required,
    unset_jwt_cookies,
    get_jwt_identity,
)
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest

from app.extensions import SessionLocal
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.user_service import UserService, \
    UserAlreadyExistsError

api_auth_bp = Blueprint('api_auth_bp', __name__)


@api_auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user.

    Expects a JSON payload with 'username', 'email', and 'password'.

    Returns:
        JSON response with a success message or error details.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")

    try:
        user_create = UserCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    with SessionLocal() as session:
        service = UserService(db=session)
        try:
            new_user = service.create_user(user_create=user_create)
            if new_user:
                return jsonify({
                    "message": "Signup successful! Please log in."
                }), 201
            return jsonify(
                {"error": "Email or username already in use."}
            ), 409
        except UserAlreadyExistsError as e:
            return jsonify({"error": str(e)}), 409
        except SQLAlchemyError as e:
            current_app.logger.error(f"Signup DB error: {e}")
            return jsonify(
                {"error": "Database error occurred."}
            ), 500
        except Exception as e:
            current_app.logger.error(f"Signup error: {e}")
            return jsonify(
                {"error": "An unexpected error occurred."}
            ), 500


@api_auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate an existing user and issue JWT tokens.

    Expects a JSON payload with 'email' and 'password'.

    Returns:
        JSON response with a success message and sets JWT cookies or error details.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")

    try:
        user_login = UserLogin.model_validate(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    with SessionLocal() as session:
        service = UserService(db=session)
        try:
            user = service.authenticate_user(email=user_login.email,
                                             password=user_login.password)
            if user and user.id:
                access_token = create_access_token(
                    identity=str(user.id))
                refresh_token = create_refresh_token(
                    identity=str(user.id))

                response = jsonify({"message": "Login successful!"})
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                return response, 200
            return jsonify(
                {"error": "Invalid email or password."}
            ), 401
        except SQLAlchemyError as e:
            current_app.logger.error(f"Login DB error: {e}")
            return jsonify(
                {"error": "Database error occurred."}
            ), 500
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            return jsonify(
                {"error": "Unexpected error occurred."}
            ), 500


@api_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh the access token using a valid refresh token.

    Returns:
        JSON response with a success message and sets a new access token cookie or error details.
    """
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify(
                {"error": "No user identity in token."}), 401

        new_access_token = create_access_token(identity=user_id)
        response = jsonify(
            {"message": "Token refreshed successfully."})
        set_access_cookies(response, new_access_token)
        return response, 200
    except Exception as e:
        current_app.logger.error(f"Error refreshing token: {e}")
        return jsonify({"error": "Token refresh failed."}), 500


@api_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Log out the current user by unsetting JWT cookies.

    Returns:
        JSON response with a success message.
    """
    response = jsonify({"message": "Logged out successfully."})
    unset_jwt_cookies(response)
    return response, 200
