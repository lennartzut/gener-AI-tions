from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required
from app.services.user_service import UserService
from app.extensions import SessionLocal
from app.utils.decorators import admin_required
from app.schemas.user_schema import UserOut
from app.models.user_model import User

api_admin_bp = Blueprint('api_admin_bp', __name__)


@api_admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """
    Admins can retrieve a list of all users.
    """
    try:
        # Optional: Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        with SessionLocal() as session:
            service = UserService(db=session)
            users_query = session.query(User)
            total = users_query.count()
            users = users_query.offset((page - 1) * per_page).limit(
                per_page).all()

            # Serialize users with Pydantic
            users_data = [UserOut.from_orm(user).model_dump() for
                          user in users]

            return jsonify({
                "total": total,
                "page": page,
                "per_page": per_page,
                "users": users_data
            }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching users: {e}")
        return jsonify({
                           "error": "An error occurred while fetching users."}), 500
