import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.extensions import SessionLocal
from app.schemas.relationship_schema import RelationshipCreate, \
    RelationshipUpdate
from app.services.relationship_service import RelationshipService
from app.utils.auth import validate_token_and_get_user
from app.utils.project import get_project_or_404

logger = logging.getLogger(__name__)

api_relationships_bp = Blueprint("api_relationships_bp", __name__)


@api_relationships_bp.route("/", methods=["POST"])
@jwt_required()
def create_relationship():
    """
    Create a new relationship between two individuals within a project.

    Query Parameters:
        project_id (int): The ID of the project.

    Expects:
        JSON payload conforming to the RelationshipCreate schema.

    Returns:
        JSON response with a success message and the created relationship data or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json() or {}
    try:
        relationship_create = RelationshipCreate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service = RelationshipService(db=session)
        try:
            new_rel = service.create_relationship(
                relationship_create, project_id)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

        if new_rel:
            return jsonify({
                "message": "Relationship created successfully.",
                "data": _short_relationship_dict(new_rel)
            }), 201
        return jsonify(
            {"error": "Failed to create relationship."}), 400


@api_relationships_bp.route("/", methods=["GET"])
@jwt_required()
def list_relationships():
    """
    List all relationships associated with a specific project.

    Query Parameters:
        project_id (int): The ID of the project.

    Returns:
        JSON response containing a list of relationships or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service = RelationshipService(db=session)
        relationships = service.list_relationships(project_id)
        relationships_out = [_short_relationship_dict(rel) for rel in
                             relationships]

    return jsonify({"relationships": relationships_out}), 200


@api_relationships_bp.route("/<int:relationship_id>",
                            methods=["GET"])
@jwt_required()
def get_relationship(relationship_id):
    """
    Retrieve details of a specific relationship by its ID.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        relationship_id (int): The unique ID of the relationship.

    Returns:
        JSON response containing the relationship details or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service = RelationshipService(db=session)
        rel = service.get_relationship_by_id(relationship_id)
        if not rel or rel.project_id != project_id:
            return jsonify({"error": "Relationship not found."}), 404

    return jsonify({"data": _short_relationship_dict(rel)}), 200


@api_relationships_bp.route("/<int:relationship_id>",
                            methods=["PATCH"])
@jwt_required()
def update_relationship(relationship_id):
    """
    Update the details of an existing relationship.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        relationship_id (int): The unique ID of the relationship to update.

    Expects:
        JSON payload conforming to the RelationshipUpdate schema.

    Returns:
        JSON response with a success message and the updated relationship data or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json()
    try:
        relationship_update = RelationshipUpdate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service = RelationshipService(db=session)
        try:
            updated_rel = service.update_relationship(
                relationship_id, relationship_update, project_id)
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

        if not updated_rel:
            return jsonify({
                               "error": "Relationship not found or update failed"}), 404

        return jsonify({
            "message": "Relationship updated successfully",
            "data": _short_relationship_dict(updated_rel)
        }), 200


@api_relationships_bp.route("/<int:relationship_id>",
                            methods=["DELETE"])
@jwt_required()
def delete_relationship(relationship_id):
    """
    Delete a specific relationship by its ID.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        relationship_id (int): The unique ID of the relationship to delete.

    Returns:
        JSON response with a success message or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service = RelationshipService(db=session)
        success = service.delete_relationship(relationship_id,
                                              project_id)
        if success:
            return jsonify({
                               "message": "Relationship deleted successfully."}), 200
        return jsonify(
            {"error": "Failed to delete relationship."}), 400


def _short_relationship_dict(rel: "Relationship"):
    """
    Generate a minimal dictionary representation of a Relationship.

    Args:
        rel (Relationship): The Relationship object.

    Returns:
        dict: A dictionary containing key relationship details.
    """
    return {
        "id": rel.id,
        "initial_relationship": rel.initial_relationship,
        "relationship_detail": rel.relationship_detail_horizontal or rel.relationship_detail_vertical,
        "notes": rel.notes,
        "union_date": rel.union_date,
        "union_place": rel.union_place,
        "dissolution_date": rel.dissolution_date,
        "created_at": rel.created_at,
        "updated_at": rel.updated_at,
        "individual": {
            "id": rel.individual.id,
            "first_name": rel.individual.first_name,
            "last_name": rel.individual.last_name,
            "relationship_id": rel.id
        },
        "related": {
            "id": rel.related.id,
            "first_name": rel.related.first_name,
            "last_name": rel.related.last_name,
            "relationship_id": rel.id
        }
    }
