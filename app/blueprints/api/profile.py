from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.schemas.user_schema import UserOut
from app.extensions import db

api_profile_bp = Blueprint('api_profile_bp', __name__)


@api_profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User retrieved successfully',
                    'data': UserOut.from_orm(
                        user).model_dump()}), 200


@api_profile_bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully',
                        'data': UserOut.from_orm(
                            user).model_dump()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating profile: {e}")
        return jsonify({
                           'error': 'An error occurred while updating the profile'}), 500


@api_profile_bp.route('/', methods=['DELETE'])
@jwt_required()
def delete_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify(
            {'message': 'User account deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {e}")
        return jsonify({
                           'error': 'An error occurred while deleting the user'}), 500
