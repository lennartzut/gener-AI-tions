import logging

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import SessionLocal
from app.schemas.user_schema import UserUpdate, UserOut
from app.services.user_service import UserService, \
    UserAlreadyExistsError
from app.utils.request_helpers import get_current_user_id_or_401

logger = logging.getLogger(__name__)

api_users_bp = Blueprint('api_users_bp', __name__)


@api_users_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_current_user_id_or_401()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    try:
        with SessionLocal() as session:
            service = UserService(db=session)
            user = service.get_user_by_id(user_id)
            if not user:
                raise NotFound("User not found.")
            user_data = UserOut.model_validate(user).model_dump()
            return jsonify({"user": user_data}), 200
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Get profile error: {e}")
        return jsonify({
                           "error": "An error occurred fetching the profile."}), 500


@api_users_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_current_user_id_or_401()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")

    try:
        user_update = UserUpdate.model_validate(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if user_update.password and user_update.confirm_password:
        user_update.confirm_password = None

    if not (
            user_update.email or user_update.username or user_update.password):
        return jsonify({"message": "No changes provided."}), 200

    try:
        with SessionLocal() as session:
            service = UserService(db=session)
            updated_user = service.update_user(user_id=user_id,
                                               user_update=user_update)
            if updated_user:
                return jsonify({
                                   "message": "Profile updated successfully."}), 200
            else:
                return jsonify(
                    {"error": "Failed to update profile."}), 409
    except UserAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except SQLAlchemyError as e:
        current_app.logger.error(f"Profile update DB error: {e}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        current_app.logger.error(f"Profile update error: {e}")
        return jsonify({"error": "Unexpected error occurred."}), 500


@api_users_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_profile():
    try:
        user_id = get_current_user_id_or_401()
    except Exception as e:
        return jsonify({"error": str(e)}), 401

    try:
        with SessionLocal() as session:
            service = UserService(db=session)
            success = service.delete_user(user_id=user_id)
            if success:
                return jsonify({
                                   "message": "Account deleted successfully."}), 200
            else:
                return jsonify(
                    {"error": "Failed to delete account."}), 400
    except SQLAlchemyError as e:
        current_app.logger.error(f"Delete profile DB error: {e}")
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        current_app.logger.error(f"Delete profile error: {e}")
        return jsonify({
                           "error": "An error occurred deleting the account."}), 500
