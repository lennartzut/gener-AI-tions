import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.extensions import SessionLocal
from app.schemas.identity_schema import IdentityCreate, \
    IdentityUpdate, IdentityOut
from app.services.identity_service import IdentityService
from app.utils.auth_utils import validate_token_and_get_user
from app.utils.project_utils import get_project_or_404

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
        try:
            new_identity = service_identity.create_identity(
                identity_create,
                is_primary=data.get('is_primary', False)
            )
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

        if new_identity:
            return jsonify({
                "message": "Identity created successfully",
                "data": IdentityOut.model_validate(
                    new_identity).model_dump()
            }), 201

        return jsonify({"error": "Failed to create identity."}), 400


@api_identities_bp.route('/', methods=['GET'])
@jwt_required()
def list_identities():
    """
    List all identities for a project.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        identities = service_identity.get_all_identities(
            project_id=project_id)
        identities_out = [
            IdentityOut.model_validate(identity).model_dump() for identity
            in identities
        ]

    return jsonify({"identities": identities_out}), 200


@api_identities_bp.route('/<int:identity_id>', methods=['GET'])
@jwt_required()
def get_identity(identity_id):
    """
    Get details of a specific identity.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        identity = service_identity.get_identity_by_id(identity_id)
        if not identity:
            return jsonify({"error": "Identity not found."}), 404

    return jsonify(
        {"data": IdentityOut.model_validate(identity).model_dump()}), 200


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
        try:
            updated_identity = service_identity.update_identity(
                identity_id, identity_update)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        if updated_identity:
            return jsonify({
                "message": "Identity updated successfully",
                "data": IdentityOut.model_validate(
                    updated_identity).model_dump()
            }), 200
        return jsonify({"error": "Failed to update identity."}), 400


@api_identities_bp.route('/<int:identity_id>', methods=['DELETE'])
@jwt_required()
def delete_identity(identity_id):
    """
    Delete an identity by ID.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        if service_identity.delete_identity(identity_id):
            return jsonify(
                {"message": "Identity deleted successfully."}), 200
        return jsonify({"error": "Failed to delete identity."}), 400
