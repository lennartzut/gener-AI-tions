import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound

from app.extensions import SessionLocal
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, \
    ProjectOut
from app.services.project_service import ProjectService
from app.utils.auth import validate_token_and_get_user

logger = logging.getLogger(__name__)

api_projects_bp = Blueprint('api_projects_bp', __name__)


@api_projects_bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    """
    Create a new project for the current user.

    Expects:
        JSON payload conforming to the ProjectCreate schema.

    Returns:
        JSON response with a success message and the created project data or error details.
    """
    user_id = validate_token_and_get_user()

    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided")

    try:
        project_create = ProjectCreate.model_validate(data)
    except ValidationError as e:
        logger.error(
            f"Validation error during project creation: {e}")
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service = ProjectService(db=session)
        try:
            new_project = service.create_project(user_id=user_id,
                                                 project_create=project_create)
            if new_project:
                project_out = ProjectOut.model_validate(
                    new_project).model_dump()
                return jsonify({
                    "message": "Project created successfully.",
                    "project": project_out
                }), 201
            return jsonify({
                "error": "Project creation failed. Possibly a project with this name already exists."
            }), 409
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project creation: {e}")
            return jsonify({
                "error": "An error occurred while creating the project."
            }), 500


@api_projects_bp.route('/', methods=['GET'])
@jwt_required()
def list_projects():
    """
    List all projects associated with the current user.

    Returns:
        JSON response containing a list of projects or error details.
    """
    user_id = validate_token_and_get_user()

    with SessionLocal() as session:
        service = ProjectService(db=session)
        try:
            projects = service.get_projects_by_user(user_id=user_id)
            projects_out = [
                ProjectOut.model_validate(project).model_dump() for
                project in projects]
            return jsonify({"projects": projects_out}), 200
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project listing: {e}")
            return jsonify({
                "error": "An error occurred while fetching projects."
            }), 500


@api_projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """
    Retrieve details of a specific project by its ID.

    Args:
        project_id (int): The unique ID of the project.

    Returns:
        JSON response containing the project details or error details.
    """
    user_id = validate_token_and_get_user()
    with SessionLocal() as session:
        service = ProjectService(db=session)
        try:
            project = service.get_project_by_id(
                project_id=project_id)
            if not project or project.user_id != user_id:
                raise NotFound("Project not found.")
            project_out = ProjectOut.model_validate(
                project).model_dump()
            return jsonify({"project": project_out}), 200
        except NotFound as e:
            logger.warning(f"Project not found: {e}")
            return jsonify({"error": str(e)}), 404
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project retrieval: {e}")
            return jsonify({
                "error": "An error occurred while fetching the project."
            }), 500


@api_projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """
    Update the details of an existing project.

    Args:
        project_id (int): The unique ID of the project to update.

    Expects:
        JSON payload conforming to the ProjectUpdate schema.

    Returns:
        JSON response with a success message and the updated project data or error details.
    """
    user_id = validate_token_and_get_user()
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided")

    try:
        project_update = ProjectUpdate.model_validate(data)
    except ValidationError as e:
        logger.error(f"Validation error during project update: {e}")
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service = ProjectService(db=session)
        try:
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
            return jsonify({
                "error": "Failed to update project. Possibly name is in use or project not found."
            }), 409
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project update: {e}")
            return jsonify({
                "error": "An error occurred while updating the project."
            }), 500


@api_projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """
    Delete a specific project by its ID.

    Args:
        project_id (int): The unique ID of the project to delete.

    Returns:
        JSON response with a success message or error details.
    """
    user_id = validate_token_and_get_user()
    with SessionLocal() as session:
        service = ProjectService(db=session)
        try:
            success = service.delete_project(project_id=project_id,
                                             user_id=user_id)
            if success:
                return jsonify({
                    "message": "Project deleted successfully."
                }), 200
            return jsonify({
                "error": "Failed to delete project or no permission."
            }), 400
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project deletion: {e}")
            return jsonify({
                "error": "An error occurred while deleting the project."
            }), 500
