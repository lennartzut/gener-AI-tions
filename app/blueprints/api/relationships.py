import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from app.extensions import SessionLocal
from app.schemas.relationship_schema import RelationshipCreate, RelationshipUpdate, RelationshipOut
from app.schemas.individual_schema import IndividualOut
from app.services.relationship_service import RelationshipService
from app.utils.project_utils import get_project_or_404
from app.utils.auth_utils import validate_token_and_get_user

logger = logging.getLogger(__name__)

api_relationships_bp = Blueprint('api_relationships_bp', __name__)


@api_relationships_bp.route('/individual/<int:individual_id>', methods=['GET'])
@jwt_required()
def get_relationships(individual_id):
    """
    Get all relationships for a specific individual within a project.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service = RelationshipService(session)
        relationships = service.get_relationships_for_individual(project_id, individual_id)

        relationships_out = []
        for rel in relationships:
            relationship_data = RelationshipOut.from_orm(rel).model_dump()
            relationship_data['individual'] = IndividualOut.from_orm(rel.individual).model_dump()
            relationship_data['related'] = IndividualOut.from_orm(rel.related).model_dump()
            relationships_out.append(relationship_data)

        return jsonify({"relationships": relationships_out}), 200


@api_relationships_bp.route('/', methods=['POST'])
@jwt_required()
def create_relationship():
    """
    Create a new relationship between two individuals.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json() or {}
    try:
        relationship_create = RelationshipCreate.model_validate(data)
        logger.debug(f"Validated relationship_create: {relationship_create}")
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service = RelationshipService(session)
        try:
            new_relationship = service.create_relationship(relationship_create, project_id)
            if new_relationship:
                return jsonify({
                    "message": "Relationship created successfully",
                    "data": RelationshipOut.from_orm(new_relationship).model_dump()
                }), 201
            return jsonify({"error": "Failed to create relationship."}), 400
        except Exception as e:
            logger.error(f"Unhandled exception: {e}")
            return jsonify({"error": "An unexpected error occurred."}), 500


@api_relationships_bp.route('/', methods=['PATCH'])
@jwt_required()
def update_relationship():
    """
    Update details of a specific relationship.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json() or {}
    try:
        relationship_update = RelationshipUpdate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    relationship_id = data.get('relationship_id')
    if not relationship_id:
        return jsonify({"error": "relationship_id is required."}), 400

    with SessionLocal() as session:
        service = RelationshipService(session)
        updated_relationship = service.update_relationship(relationship_id, relationship_update, project_id)
        if updated_relationship:
            return jsonify({
                "message": "Relationship updated successfully",
                "data": RelationshipOut.from_orm(updated_relationship).model_dump()
            }), 200
        return jsonify({"error": "Failed to update relationship."}), 400


@api_relationships_bp.route('/<int:relationship_id>', methods=['DELETE'])
@jwt_required()
def delete_relationship(relationship_id):
    """
    Delete a specific relationship by its ID.
    """
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    with SessionLocal() as session:
        service = RelationshipService(session)
        success = service.delete_relationship(relationship_id, project_id)
        if success:
            return jsonify({"message": "Relationship deleted successfully."}), 200
        return jsonify({"error": "Failed to delete relationship."}), 400