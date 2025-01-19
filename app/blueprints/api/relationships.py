import logging

from flask import Blueprint, request, g
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound, \
    InternalServerError

from app.extensions import SessionLocal
from app.schemas.relationship_schema import RelationshipCreate, \
    RelationshipUpdate
from app.services.relationship_service import RelationshipService
from app.utils.response_helpers import success_response
from app.utils.security_decorators import require_project_access

logger = logging.getLogger(__name__)

api_relationships_bp = Blueprint("api_relationships_bp", __name__)


@api_relationships_bp.route("/", methods=["POST"])
@require_project_access
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
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        relationship_create = RelationshipCreate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_relationship = RelationshipService(db=session)
        try:
            new_relationship = service_relationship.create_relationship(
                relationship_create, g.project_id
            )
            if not new_relationship:
                raise BadRequest("Failed to create relationship.")
            return success_response(
                "Relationship created successfully.",
                {"data": _short_relationship_dict(new_relationship)},
                201
            )
        except ValueError as ve:
            raise BadRequest(str(ve))
        except SQLAlchemyError as e:
            logger.error(f"Error creating relationship: {e}")
            raise InternalServerError("Database error occurred.")


@api_relationships_bp.route("/", methods=["GET"])
@require_project_access
def list_relationships():
    """
    List all relationships associated with a specific project.

    Query Parameters:
        project_id (int): The ID of the project.

    Returns:
        JSON response containing a list of relationships or error details.
    """
    with SessionLocal() as session:
        service_relationship = RelationshipService(db=session)
        try:
            rels = service_relationship.list_relationships(
                g.project_id)
            relationship_out = [_short_relationship_dict(r) for r in
                                rels]
            return success_response(
                "Relationships fetched successfully.",
                {"relationships": relationship_out}
            )
        except SQLAlchemyError as e:
            logger.error(f"Error listing relationships: {e}")
            raise InternalServerError("Database error occurred.")


@api_relationships_bp.route("/<int:relationship_id>",
                            methods=["GET"])
@require_project_access
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
    with SessionLocal() as session:
        service_relationship = RelationshipService(db=session)
        try:
            relationship = service_relationship.get_relationship_by_id(
                relationship_id)
            if not relationship or relationship.project_id != g.project_id:
                raise NotFound("Relationship not found.")
            return success_response(
                "Relationship fetched successfully.",
                {"data": _short_relationship_dict(relationship)}
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving relationship: {e}")
            raise InternalServerError("Database error occurred.")


@api_relationships_bp.route("/<int:relationship_id>",
                            methods=["PATCH"])
@require_project_access
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
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        relationship_update = RelationshipUpdate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_relationship = RelationshipService(db=session)
        try:
            updated_rel = service_relationship.update_relationship(
                relationship_id, relationship_update, g.project_id
            )
            if not updated_rel:
                raise NotFound(
                    "Relationship not found or update failed.")
            return success_response(
                "Relationship updated successfully",
                {"data": _short_relationship_dict(updated_rel)}
            )
        except ValueError as ve:
            raise BadRequest(str(ve))
        except SQLAlchemyError as e:
            logger.error(f"Error updating relationship: {e}")
            raise InternalServerError("Database error occurred.")


@api_relationships_bp.route("/<int:relationship_id>",
                            methods=["DELETE"])
@require_project_access
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
    with SessionLocal() as session:
        service_relationship = RelationshipService(db=session)
        try:
            success = service_relationship.delete_relationship(
                relationship_id, g.project_id)
            if success:
                return success_response(
                    "Relationship deleted successfully.")
            raise BadRequest("Failed to delete relationship.")
        except ValueError as ve:
            raise BadRequest(str(ve))
        except SQLAlchemyError as e:
            logger.error(f"Error deleting relationship: {e}")
            raise InternalServerError("Database error occurred.")


def _short_relationship_dict(rel):
    return {
        "id": rel.id,
        "initial_relationship": rel.initial_relationship,
        "relationship_detail": (
                rel.relationship_detail_horizontal or rel.relationship_detail_vertical
        ),
        "notes": rel.notes,
        "union_date": rel.union_date,
        "union_place": rel.union_place,
        "dissolution_date": rel.dissolution_date,
        "created_at": rel.created_at,
        "updated_at": rel.updated_at,
        "individual": {
            "id": rel.individual.id,
            "first_name": rel.individual.first_name,
            "last_name": rel.individual.last_name
        },
        "related": {
            "id": rel.related.id,
            "first_name": rel.related.first_name,
            "last_name": rel.related.last_name
        }
    }
