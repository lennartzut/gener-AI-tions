import logging

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest, Conflict, \
    InternalServerError

from app.extensions import SessionLocal
from app.schemas.user_schema import UserUpdate, UserOut
from app.services.user_service import UserService, \
    UserAlreadyExistsError
from app.utils.auth_utils import get_current_user_id
from app.utils.response_helpers import success_response

logger = logging.getLogger(__name__)

api_users_bp = Blueprint('api_users_bp', __name__)


@api_users_bp.route('/', methods=['GET'])
@jwt_required()
def get_user():
    """
    Retrieve the current user's profile.
    """
    try:
        user_id = get_current_user_id()
    except Exception as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_user = UserService(db=session)
        try:
            user = service_user.get_user_by_id(user_id)
            if not user:
                raise NotFound("User not found.")
            user_data = UserOut.model_validate(user).model_dump()
            return success_response("User fetched successfully.",
                                    {"user": user_data})
        except SQLAlchemyError as e:
            current_app.logger.error(f"Get profile error: {e}")
            raise InternalServerError(
                "An error occurred fetching the profile.")


@api_users_bp.route('/', methods=['PATCH'])
@jwt_required()
def update_user():
    """
    Update the current user's profile.
    Expects JSON payload conforming to the UserUpdate schema.
    """
    try:
        user_id = get_current_user_id()
    except Exception as e:
        raise BadRequest(str(e))

    if not request.is_json:
        raise BadRequest("Invalid content type. JSON expected.")

    data = request.get_json()
    if not data:
        raise BadRequest("Empty or invalid JSON payload.")

    try:
        user_update = UserUpdate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_user = UserService(db=session)
        try:
            updated_user = service_user.update_user(user_id=user_id,
                                                    user_update=user_update)
            if updated_user:
                return success_response(
                    "Profile updated successfully.",
                    {"user": UserOut.model_validate(
                        updated_user).model_dump()}, 200)
            raise Conflict("Failed to update profile.")
        except UserAlreadyExistsError as e:
            raise Conflict(f"{e.message} ({e.field})")
        except SQLAlchemyError as e:
            current_app.logger.error(f"Profile update DB error: {e}")
            raise InternalServerError("Database error occurred.")


@api_users_bp.route('/', methods=['DELETE'])
@jwt_required()
def delete_user():
    """
    Delete the current user's account.
    """
    try:
        user_id = get_current_user_id()
    except Exception as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_user = UserService(db=session)
        try:
            success = service_user.delete_user(user_id=user_id)
            if success:
                return success_response(
                    "Account deleted successfully.", status_code=200)
            raise BadRequest("Failed to delete account.")
        except SQLAlchemyError as e:
            current_app.logger.error(f"Delete profile DB error: {e}")
            raise InternalServerError("Database error occurred.")
