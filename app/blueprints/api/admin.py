from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required

from app.extensions import SessionLocal
from app.models.user_model import User
from app.schemas.user_schema import UserOut
from app.services.user_service import UserService
from app.utils.security_decorators import admin_required

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
        JSON response containing the total number of users, current page,
        users per page, and a list of user data.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        with SessionLocal() as session:
            service = UserService(db=session)
            users = service.get_paginated_users(page=page,
                                                per_page=per_page)
            total = session.query(User).count()

            users_out = [UserOut.model_validate(user).model_dump()
                         for user in users]

            return jsonify({
                "total": total,
                "page": page,
                "per_page": per_page,
                "users": users_out
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching users: {e}")
        return jsonify({
            "error": "An error occurred while fetching users."
        }), 500
