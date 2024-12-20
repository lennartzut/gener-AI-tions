from flask import Blueprint, jsonify, request, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.family_schema import FamilyCreate, FamilyUpdate, \
    FamilyOut
from app.extensions import db
from app.services.project_service import ProjectService
from app.services.family_service import FamilyService

api_families_bp = Blueprint('api_families', __name__)


def get_project_or_404(user_id: int, project_id: int):
    service = ProjectService(db=db.session)
    project = service.get_project_by_id(project_id)
    if not project or project.user_id != user_id:
        abort(404,
              description="Project not found or not owned by this user.")
    return project


@api_families_bp.route('/', methods=['GET'])
@jwt_required()
def list_families():
    """List all families for a project."""
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)
    try:
        service = FamilyService(db=db.session)
        families = service.list_families_by_project(project_id)
        results = [FamilyOut.from_orm(f).model_dump() for f in
                   families]
        return jsonify({"data": results}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(f"DB error listing families: {e}")
        return jsonify({"error": "Database error"}), 500


@api_families_bp.route('/<int:family_id>', methods=['GET'])
@jwt_required()
def get_family(family_id):
    """Retrieve details of a specific family."""
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)
    try:
        service = FamilyService(db=db.session)
        family = service.get_family_by_id(family_id)
        if not family or family.project_id != project_id:
            return jsonify({'error': 'Family not found'}), 404

        return jsonify(
            {"data": FamilyOut.from_orm(family).model_dump()}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"DB error retrieving family {family_id}: {e}")
        return jsonify({"error": "Database error"}), 500


@api_families_bp.route('/', methods=['POST'])
@jwt_required()
def create_family():
    """Create a new family."""
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)
    try:
        data = request.get_json() or {}
        family_data = FamilyCreate(**data)
        service = FamilyService(db=db.session)
        new_family = service.create_family(project_id=project_id,
                                           **family_data.dict())
        return jsonify({
            "message": "Family created successfully",
            "data": FamilyOut.from_orm(new_family).model_dump()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"DB error creating family: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating family: {e}")
        return jsonify({"error": "Invalid data"}), 400


@api_families_bp.route('/<int:family_id>', methods=['PUT'])
@jwt_required()
def update_family(family_id):
    """Update an existing family."""
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)
    try:
        service = FamilyService(db=db.session)
        family = service.get_family_by_id(family_id)
        if not family or family.project_id != project_id:
            return jsonify({"error": "Family not found"}), 404

        data = request.get_json() or {}
        family_update = FamilyUpdate(**data)
        updated_family = service.update_family(family_id,
                                               **family_update.dict(
                                                   exclude_unset=True))

        return jsonify({"message": "Family updated successfully",
                        "data": FamilyOut.from_orm(
                            updated_family).model_dump()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"DB error updating family {family_id}: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating family: {e}")
        return jsonify({"error": "Invalid data"}), 400


@api_families_bp.route('/<int:family_id>', methods=['DELETE'])
@jwt_required()
def delete_family(family_id):
    """Delete a family."""
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)
    try:
        service = FamilyService(db=db.session)
        deleted_family = service.delete_family(family_id)
        if not deleted_family:
            return jsonify({"error": "Family not found"}), 404

        return jsonify(
            {"message": "Family deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"DB error deleting family {family_id}: {e}")
        return jsonify({"error": "Database error"}), 500
