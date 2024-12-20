from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, \
    ProjectOut
from app.services.project_service import ProjectService

api_projects_bp = Blueprint('api_projects_bp', __name__)


@api_projects_bp.route('/projects', methods=['GET'])
@jwt_required()
def list_projects():
    current_user_id = get_jwt_identity()
    service = ProjectService(db=db.session)
    projects = service.get_projects_by_user(current_user_id)
    return jsonify({"data": [ProjectOut.from_orm(p).dict() for p in
                             projects]}), 200


@api_projects_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = get_jwt_identity()
    try:
        data = request.get_json() or {}
        project_data = ProjectCreate(**data)
        service = ProjectService(db=db.session)
        new_project = service.create_project(user_id=current_user_id,
                                             name=project_data.name)
        return jsonify({"message": "Project created successfully",
                        "data": ProjectOut.from_orm(
                            new_project).dict()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error on create_project: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Create project error: {e}")
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    current_user_id = get_jwt_identity()
    service = ProjectService(db=db.session)
    project = service.get_project_by_id(project_id)
    if not project or project.user_id != int(current_user_id):
        return jsonify(
            {"error": "Project not found or not owned by you"}), 404
    try:
        data = request.get_json() or {}
        project_update = ProjectUpdate(**data)
        updated_project = service.update_project(project_id,
                                                 project_update.name) if project_update.name else project
        if updated_project:
            return jsonify(
                {"message": "Project updated successfully",
                 "data": ProjectOut.from_orm(
                     updated_project).dict()}), 200
        return jsonify(
            {"error": "Project not found or already deleted"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error on update_project: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Update project error: {e}")
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_projects_bp.route('/projects/<int:project_id>',
                       methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    current_user_id = get_jwt_identity()
    service = ProjectService(db=db.session)
    project = service.get_project_by_id(project_id)
    if not project or project.user_id != int(current_user_id):
        return jsonify(
            {"error": "Project not found or not owned by you"}), 404
    try:
        deleted_project = service.soft_delete_project(project_id)
        if deleted_project:
            return jsonify(
                {"message": "Project deleted successfully"}), 200
        else:
            return jsonify({
                               "error": "Project not found or already deleted"}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error on delete_project: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Delete project error: {e}")
        return jsonify(
            {"error": "Unexpected error", "details": str(e)}), 400
