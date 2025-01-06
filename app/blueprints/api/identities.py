import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from app.extensions import SessionLocal
from app.schemas.identity_schema import IdentityCreate, IdentityUpdate, IdentityOut
from app.services.identity_service import IdentityService
from app.utils.project_utils import get_project_or_404
from app.utils.auth_utils import validate_token_and_get_user

logger = logging.getLogger(__name__)

api_identities_bp = Blueprint('api_identities_bp', __name__)


@api_identities_bp.route('/', methods=['POST'])
@jwt_required()
def create_identity():
    """
    Create a new identity for an individual.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json() or {}
    try:
        identity_create = IdentityCreate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        new_identity = service_identity.create_identity(identity_create, is_primary=data.get('is_primary', False))
        if new_identity:
            return jsonify({
                "message": "Identity created successfully",
                "data": IdentityOut.from_orm(new_identity).model_dump()
            }), 201
        return jsonify({"error": "Failed to create identity."}), 400


@api_identities_bp.route('/<int:identity_id>', methods=['PATCH'])
@jwt_required()
def update_identity(identity_id):
    """
    Update an existing identity's details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)
    data = request.get_json() or {}

    try:
        identity_update = IdentityUpdate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        updated_identity = service_identity.update_identity(identity_id, identity_update)
        if updated_identity:
            return jsonify({
                "message": "Identity updated successfully",
                "data": IdentityOut.from_orm(updated_identity).model_dump()
            }), 200
        return jsonify({"error": "Failed to update identity."}), 400
