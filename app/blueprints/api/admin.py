import logging

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError

from app.extensions import SessionLocal
from app.models.user_model import User
from app.schemas.user_schema import UserOut
from app.services.user_service import UserService
from app.utils.response_helpers import success_response
from app.utils.security_decorators import admin_required

logger = logging.getLogger(__name__)

api_admin_bp = Blueprint('api_admin_bp', __name__)


@api_admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """
    Retrieve a paginated list of all users. Accessible only to admins.
    Query Parameters:
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): The number of users per page. Defaults to 20.
    Returns:
        JSON response containing total, page, per_page and list of user data.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    try:
        with SessionLocal() as session:
            service_user = UserService(db=session)
            users = service_user.get_paginated_users(page=page,
                                                     per_page=per_page)
            total = session.query(User).count()
            # Convert each ORM object into a schema-dict using UserOut.
            users_out = [UserOut.model_validate(u).model_dump() for u
                         in users]
            return success_response(
                "Users fetched successfully.",
                {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "users": users_out
                },
                200
            )
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching users: {e}")
        raise InternalServerError("Database error occurred.")
