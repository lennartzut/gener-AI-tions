from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.models.identity import Identity
from app.models.individual import Individual
from app.models.project import Project
from app.schemas.identity_schema import IdentityCreate, \
    IdentityUpdate, IdentityOut
from app.extensions import db

api_identities_bp = Blueprint('api_identities_bp', __name__)


def get_project_or_404(user_id: int, project_id: int) -> Project:
    project = Project.query.filter_by(id=project_id,
                                      user_id=user_id).first()
    if not project:
        from flask import abort
        abort(404, "Project not found or not owned by this user.")
    return project


@api_identities_bp.route('/', methods=['POST'])
@jwt_required()
def create_identity():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_project_or_404(current_user_id, project_id)
    try:
        data = request.get_json() or {}
        identity_data = IdentityCreate(**data)
        individual = Individual.query.filter_by(
            id=identity_data.individual_id, user_id=current_user_id,
            project_id=project_id).first()
        if not individual:
            return jsonify({
                               "error": "Individual not found or not owned by the user."}), 404
        new_identity = Identity(
            individual_id=individual.id,
            first_name=identity_data.first_name,
            last_name=identity_data.last_name,
            gender=identity_data.gender,
            valid_from=identity_data.valid_from,
            valid_until=identity_data.valid_until
        )
        db.session.add(new_identity)
        db.session.commit()
        return jsonify({"message": "Identity created successfully",
                        "data": IdentityOut.from_orm(
                            new_identity).model_dump()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"DB error creating identity: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating identity: {e}")
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_identities_bp.route('/<int:identity_id>', methods=['PUT'])
@jwt_required()
def update_identity(identity_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_project_or_404(current_user_id, project_id)
    try:
        identity = Identity.query.get(identity_id)
        if not identity or identity.individual.user_id != current_user_id or identity.individual.project_id != project_id:
            return jsonify({
                               "error": "Identity not found or not owned by this user."}), 404
        data = request.get_json() or {}
        identity_update = IdentityUpdate(**data)
        for k, v in identity_update.dict(exclude_unset=True).items():
            setattr(identity, k, v)
        db.session.commit()
        return jsonify({"message": "Identity updated successfully",
                        "data": IdentityOut.from_orm(
                            identity).model_dump()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"DB error updating identity {identity_id}: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating identity: {e}")
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_identities_bp.route('/<int:identity_id>', methods=['DELETE'])
@jwt_required()
def delete_identity(identity_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_project_or_404(current_user_id, project_id)
    try:
        identity = Identity.query.get(identity_id)
        if not identity or identity.individual.user_id != current_user_id or identity.individual.project_id != project_id:
            return jsonify({
                               "error": "Identity not found or not owned by this user."}), 404
        db.session.delete(identity)
        db.session.commit()
        return jsonify(
            {"message": "Identity deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"DB error deleting identity {identity_id}: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
