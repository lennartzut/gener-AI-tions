from flask import Blueprint, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
    create_access_token, set_access_cookies
)
from models.user import User
from schemas.auth_schema import UserOut

auth_api_bp = Blueprint('auth_api', __name__)


# Current User Info
@auth_api_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    user_out = UserOut.from_orm(user)
    return jsonify(user_out.model_dump()), 200


# Refresh Token Route
@auth_api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    response = jsonify({'message': 'Token refreshed'})
    set_access_cookies(response, new_access_token)
    return response, 200
