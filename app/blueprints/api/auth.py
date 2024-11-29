from flask import Blueprint, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
    create_access_token, set_access_cookies
)
from app.models.user import User
from app.schemas import UserOut
from app.extensions import db

api_auth_bp = Blueprint('api_auth_bp', __name__)


# Current User Info
@api_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    user_out = UserOut.model_validate(user)
    return jsonify(user_out.model_dump()), 200


# Refresh Token Route
@api_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    response = jsonify({'message': 'Token refreshed'})
    set_access_cookies(response, new_access_token)
    return response, 200
