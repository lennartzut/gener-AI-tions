from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from flask_pydantic import validate
from sqlalchemy.exc import SQLAlchemyError
from app.services.user_service import UserService
from app.schemas.user_schema import UserLogin, UserCreate
from app.extensions import db

api_auth_bp = Blueprint('api_auth_bp', __name__)


@api_auth_bp.route('/login', methods=['POST'])
@validate()
def login():
    """User login endpoint."""
    try:
        data = request.get_json() or {}
        login_data = UserLogin(**data)

        user_service = UserService(db=db.session)
        user = user_service.authenticate_user(login_data.email,
                                              login_data.password)
        if not user:
            return jsonify(
                {'error': 'Invalid email or password'}), 401

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    except (ValueError, TypeError) as e:
        current_app.logger.error(
            f"Validation error during login: {e}")
        return jsonify({'error': 'Invalid login data'}), 400
    except Exception as e:
        current_app.logger.error(
            f"Unexpected error during login: {e}")
        return jsonify({'error': 'Unexpected server error'}), 500


@api_auth_bp.route('/signup', methods=['POST'])
@validate()
def signup():
    """User signup endpoint."""
    try:
        data = request.get_json() or {}
        user_data = UserCreate(**data)

        user_service = UserService(db=db.session)
        if user_service.email_or_username_exists(user_data.email,
                                                 user_data.username):
            return jsonify(
                {'error': 'Email or username already in use'}), 409

        user_service.create_user(username=user_data.username,
                                 email=user_data.email,
                                 password=user_data.password)

        return jsonify(
            {'message': 'User signed up successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error during signup: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except ValueError as ve:
        current_app.logger.error(f"Signup validation error: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected signup error: {e}")
        return jsonify({'error': 'Unexpected error occurred'}), 500


@api_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@validate()
def refresh():
    """Refresh access token using a valid refresh token."""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': access_token,
                        'message': 'Token refreshed successfully'}), 200
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Unable to refresh token'}), 500


@api_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@validate()
def logout():
    """Logout user by client-side token removal."""
    return jsonify({'message': 'Logout successful'}), 200
