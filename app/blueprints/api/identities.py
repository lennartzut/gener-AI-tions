import logging

from flask import Blueprint, request, g
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, InternalServerError, \
    NotFound

from app.extensions import SessionLocal
from app.schemas.identity_schema import IdentityCreate, \
    IdentityUpdate, IdentityOut
from app.services.identity_service import IdentityService
from app.utils.response_helpers import success_response
from app.utils.security_decorators import require_project_access

logger = logging.getLogger(__name__)

api_identities_bp = Blueprint('api_identities_bp', __name__)


@api_identities_bp.route('/', methods=['POST'])
@require_project_access
def create_identity():
    """
    Create a new identity for an individual within a project.
    Expects JSON payload conforming to IdentityCreate schema.
    Returns a JSON response with the created identity data.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        identity_create = IdentityCreate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        try:
            new_identity = service_identity.create_identity(
                identity_create=identity_create,
                is_primary=data.get('is_primary', False)
            )
            if not new_identity:
                raise BadRequest("Failed to create identity.")
            identity_out = IdentityOut.model_validate(new_identity,
                                                      from_attributes=True)
            return success_response(
                "Identity created successfully",
                {"identity": identity_out.model_dump()},
                201
            )
        except SQLAlchemyError as e:
            logger.error(f"Error creating identity: {e}")
            raise InternalServerError("Database error occurred.")


@api_identities_bp.route('/', methods=['GET'])
@require_project_access
def list_identities():
    """
    List all identities associated with a specific project.
    """
    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        try:
            identities = service_identity.get_all_identities(
                project_id=g.project_id)
            identities_out = [
                IdentityOut.model_validate(identity).model_dump() for
                identity in identities
            ]
            return success_response(
                "Identities fetched successfully.",
                {"identities": identities_out},
                200
            )
        except SQLAlchemyError as e:
            logger.error(f"Error fetching identities: {e}")
            raise InternalServerError("Database error occurred.")


@api_identities_bp.route('/<int:identity_id>', methods=['GET'])
@require_project_access
def get_identity(identity_id):
    """
    Retrieve details of a specific identity by its ID.
    """
    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        try:
            identity = service_identity.get_identity_by_id(
                identity_id)
            if not identity:
                raise NotFound("Identity not found.")
            identity_out = IdentityOut.model_validate(
                identity).model_dump()
            return success_response("Identity fetched successfully.",
                                    {"data": identity_out})
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving identity: {e}")
            raise InternalServerError("Database error occurred.")


@api_identities_bp.route('/<int:identity_id>', methods=['PATCH'])
@require_project_access
def update_identity(identity_id):
    """
    Update an existing identity.
    Expects JSON payload conforming to IdentityUpdate schema.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        identity_update = IdentityUpdate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        try:
            updated_identity = service_identity.update_identity(
                identity_id, identity_update)
            if not updated_identity:
                raise BadRequest("Failed to update identity.")
            identity_out = IdentityOut.model_validate(
                updated_identity).model_dump()
            return success_response("Identity updated successfully",
                                    {"data": identity_out})
        except SQLAlchemyError as e:
            logger.error(f"Error updating identity: {e}")
            raise InternalServerError("Database error occurred.")


@api_identities_bp.route('/<int:identity_id>', methods=['DELETE'])
@require_project_access
def delete_identity(identity_id):
    """
    Delete an identity by its ID.
    """
    with SessionLocal() as session:
        service_identity = IdentityService(db=session)
        try:
            success = service_identity.delete_identity(identity_id)
            if success:
                return success_response(
                    "Identity deleted successfully.",
                    status_code=200)
            raise BadRequest("Failed to delete identity.")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting identity: {e}")
            raise InternalServerError("Database error occurred.")
