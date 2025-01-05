import logging

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import SessionLocal
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, \
    ProjectOut
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)

api_projects_bp = Blueprint('api_projects_bp', __name__)


@api_projects_bp.route('/', methods=['GET'])
@jwt_required()
def list_projects():
    current_user_id = get_jwt_identity()
    if not current_user_id or not current_user_id.strip():
        current_app.logger.error("list_projects: empty identity")
        return jsonify({"error": "No user identity in token."}), 401

    try:
        user_id = int(current_user_id)
    except ValueError:
        current_app.logger.error(
            "list_projects: invalid user ID format")
        return jsonify({"error": "Invalid user ID in token."}), 400

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            projects = service.get_projects_by_user(user_id=user_id)
            projects_out = [
                ProjectOut.model_validate(project).model_dump() for
                project in projects]
            return jsonify({"projects": projects_out}), 200
    except Exception as e:
        current_app.logger.error(f"List projects error: {e}")
        return jsonify({
            "error": "An error occurred while fetching projects."
        }), 500


@api_projects_bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    current_user_id = get_jwt_identity()
    if not current_user_id or not str(current_user_id).strip():
        return jsonify({"error": "No user identity in token."}), 401

    try:
        user_id = int(current_user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID in token."}), 400

    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided")

    try:
        project_create = ProjectCreate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Invalid data provided."}), 400

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            new_project = service.create_project(
                user_id=user_id,
                project_create=project_create
            )
            if new_project:
                project_out = ProjectOut.model_validate(
                    new_project).model_dump()
                return jsonify({
                    "message": "Project created successfully.",
                    "project": project_out
                }), 201
            else:
                return jsonify({
                    "error": "Project creation failed. Possibly a project with this name already exists."
                }), 409
    except Exception as e:
        current_app.logger.error(f"Create project error: {e}")
        return jsonify({
            "error": "An error occurred while creating the project."
        }), 500


@api_projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    current_user_id = get_jwt_identity()
    if not current_user_id or not current_user_id.strip():
        return jsonify({"error": "No user identity in token."}), 401

    try:
        user_id = int(current_user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID in token."}), 400

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            project = service.get_project_by_id(
                project_id=project_id)
            if not project or project.user_id != user_id:
                raise NotFound("Project not found.")

            project_out = ProjectOut.model_validate(
                project).model_dump()
            return jsonify({"project": project_out}), 200
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Get project error: {e}")
        return jsonify({
            "error": "An error occurred while fetching the project."
        }), 500


@api_projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    current_user_id = get_jwt_identity()
    if not current_user_id or not str(current_user_id).strip():
        return jsonify({"error": "No user identity in token."}), 401

    try:
        user_id = int(current_user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID in token."}), 400

    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided")

    try:
        project_update = ProjectUpdate.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Invalid data provided."}), 400

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            updated_project = service.update_project(
                project_id=project_id,
                user_id=user_id,
                project_update=project_update
            )
            if updated_project:
                project_out = ProjectOut.model_validate(
                    updated_project).model_dump()
                return jsonify({
                    "message": "Project updated successfully.",
                    "project": project_out
                }), 200
            else:
                return jsonify({
                    "error": "Failed to update project. Possibly name is in use or project not found."
                }), 409
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Update project error: {e}")
        return jsonify({
                           "error": "An error occurred while updating the project."}), 500


@api_projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    current_user_id = get_jwt_identity()
    if not current_user_id or not str(current_user_id).strip():
        return jsonify({"error": "No user identity in token."}), 401

    try:
        user_id = int(current_user_id)
    except ValueError:
        return jsonify({"error": "Invalid user ID in token."}), 400

    try:
        with SessionLocal() as session:
            service = ProjectService(db=session)
            success = service.delete_project(
                project_id=project_id,
                user_id=user_id
            )
            if success:
                return jsonify({
                                   "message": "Project deleted successfully."}), 200
            else:
                return jsonify({
                    "error": "Failed to delete project or no permission."
                }), 400
    except Exception as e:
        current_app.logger.error(f"Delete project error: {e}")
        return jsonify({
            "error": "An error occurred while deleting the project."
        }), 500
