import logging

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound, Conflict, \
    InternalServerError

from app.extensions import SessionLocal
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, \
    ProjectOut
from app.services.project_service import ProjectService
from app.utils.auth_utils import get_current_user_id
from app.utils.response_helpers import success_response

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
    user_id = get_current_user_id()
    if not user_id:
        raise BadRequest("User ID is required.")
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        project_create = ProjectCreate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))
    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        try:
            new_project = service_project.create_project(
                user_id=user_id, project_create=project_create)
            if not new_project:
                raise Conflict("Failed to create project.")
            project_out = ProjectOut.model_validate(
                new_project).model_dump()
            return success_response("Project created successfully.",
                                    {"project": project_out}, 201)
        except SQLAlchemyError as e:
            logger.error(f"Error creating project: {e}")
            raise InternalServerError("Database error occurred.")


@api_projects_bp.route('/', methods=['GET'])
@jwt_required()
def list_projects():
    """
    List all projects associated with the current user.

    Returns:
        JSON response containing a list of projects or error details.
    """
    user_id = get_current_user_id()
    with SessionLocal() as session:
        service = ProjectService(db=session)
        try:
            projects = service.get_projects_by_user(user_id=user_id)
            projects_out = [ProjectOut.model_validate(p).model_dump()
                            for p in projects]
            return success_response("Projects fetched successfully.",
                                    {"projects": projects_out})
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project listing: {e}")
            raise InternalServerError("Database error occurred.")


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
    user_id = get_current_user_id()
    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        try:
            project = service_project.get_project_by_id(
                project_id=project_id)
            if not project or project.user_id != user_id:
                raise NotFound(
                    "Project not found or not owned by user.")
            project_out = ProjectOut.model_validate(
                project).model_dump()
            return success_response(
                "Project retrieved successfully.", {"project":
                                                        project_out})
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project retrieval: {e}")
            raise InternalServerError("Database error occurred.")


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
    user_id = get_current_user_id()
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        project_update = ProjectUpdate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))
    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        try:
            updated_project = service_project.update_project(
                project_id=project_id,
                user_id=user_id,
                project_update=project_update
            )
            if updated_project:
                project_out = ProjectOut.model_validate(
                    updated_project).model_dump()
                return success_response(
                    "Project updated successfully.",
                    {"project": project_out})
            raise Conflict(
                "Failed to update project. Possibly name in use or project not found.")
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project update: {e}")
            raise InternalServerError("Database error occurred.")


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
    user_id = get_current_user_id()
    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        try:
            success = service_project.delete_project(
                project_id=project_id, user_id=user_id)
            if success:
                return success_response(
                    "Project deleted successfully.")
            raise BadRequest(
                "Failed to delete project or no permission.")
        except SQLAlchemyError as e:
            logger.error(
                f"Database error during project deletion: {e}")
            raise InternalServerError("Database error occurred.")
