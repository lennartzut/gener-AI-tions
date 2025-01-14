import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.extensions import SessionLocal
from app.schemas.identity_schema import IdentityCreate, \
    IdentityUpdate, IdentityOut
from app.services.identity_service import IdentityService
from app.utils.auth import validate_token_and_get_user
from app.utils.project import get_project_or_404

logger = logging.getLogger(__name__)

api_identities_bp = Blueprint('api_identities_bp', __name__)


@api_identities_bp.route('/', methods=['POST'])
@jwt_required()
def create_identity():
    """
    Create a new identity for an individual within a project.

    Query Parameters:
        project_id (int): The ID of the project.

    Expects:
        JSON payload conforming to the IdentityCreate schema.

    Returns:
        JSON response with a success message and the created identity data or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "No input data provided."}), 400

    identity_create = IdentityCreate.model_validate(data)

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        new_identity = service_identity.create_identity(
            identity_create=identity_create,
            is_primary=data.get('is_primary', False)
        )
        if not new_identity:
            return jsonify(
                {"error": "Failed to create identity."}), 400

        identity_out = IdentityOut.model_validate(new_identity,
                                                  from_attributes=True)
        return jsonify({
            "message": "Identity created successfully",
            "data": identity_out.model_dump()
        }), 201


@api_identities_bp.route('/', methods=['GET'])
@jwt_required()
def list_identities():
    """
    List all identities associated with a specific project.

    Query Parameters:
        project_id (int): The ID of the project.

    Returns:
        JSON response containing a list of all identities or error details.
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
            IdentityOut.model_validate(identity).model_dump() for
            identity in identities
        ]

    return jsonify({"identities": identities_out}), 200


@api_identities_bp.route('/<int:identity_id>', methods=['GET'])
@jwt_required()
def get_identity(identity_id):
    """
    Retrieve details of a specific identity by its ID.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        identity_id (int): The unique ID of the identity.

    Returns:
        JSON response containing the identity details or error details.
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

    return jsonify({"data": IdentityOut.model_validate(
        identity).model_dump()}), 200


@api_identities_bp.route('/<int:identity_id>', methods=['PATCH'])
@jwt_required()
def update_identity(identity_id):
    """
    Update the details of an existing identity.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        identity_id (int): The unique ID of the identity to update.

    Expects:
        JSON payload conforming to the IdentityUpdate schema.

    Returns:
        JSON response with a success message and the updated identity data or error details.
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
    Delete an identity by its ID.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        identity_id (int): The unique ID of the identity to delete.

    Returns:
        JSON response with a success message or error details.
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
