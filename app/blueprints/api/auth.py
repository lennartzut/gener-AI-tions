from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
    create_access_token, set_access_cookies
)
from app.models.user import User
from app.schemas.user_schema import UserOut

api_auth_bp = Blueprint('api_auth_bp', __name__)


@api_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Retrieves the currently authenticated user's information.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found.'}), 404

        return jsonify({
            'message': 'User retrieved successfully',
            'data': UserOut.from_orm(user).model_dump()
        }), 200

    except Exception as e:
        current_app.logger.error(
            f"Error retrieving current user: {e}")
        return jsonify({
                           'error': 'An error occurred while retrieving user.'}), 500


@api_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    """
    Generates a new access token using a valid refresh token.
    """
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(
            identity=current_user_id)

        response = jsonify({
            'message': 'Token refreshed successfully',
            'access_token': new_access_token
        })
        set_access_cookies(response, new_access_token)
        return response, 200

    except Exception as e:
        current_app.logger.error(
            f"Error refreshing access token: {e}")
        return jsonify({
                           'error': 'An error occurred while refreshing the token.'}), 500
