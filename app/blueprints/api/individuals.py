import logging

from flask import Blueprint, request, g
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound, \
    InternalServerError

from app.extensions import SessionLocal
from app.schemas.identity_schema import IdentityIdOut
from app.schemas.individual_schema import IndividualCreate, \
    IndividualUpdate, IndividualOut
from app.services.individual_service import IndividualService
from app.utils.response_helpers import success_response
from app.utils.security_decorators import require_project_access

logger = logging.getLogger(__name__)

api_individuals_bp = Blueprint("api_individuals_bp", __name__)


@api_individuals_bp.route("/", methods=["POST"])
@require_project_access
def create_individual():
    """
    Create a new individual within a project.
    Expects JSON payload conforming to IndividualCreate schema.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        individual_create = IndividualCreate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        try:
            new_individual = service_individual.create_individual(
                user_id=g.user_id,
                project_id=g.project_id,
                individual_create=individual_create
            )
            if not new_individual:
                raise BadRequest("Failed to create individual.")
            individual_out = IndividualOut.model_validate(
                new_individual, from_attributes=True)
            individual_out.identities = [
                IdentityIdOut(id=identity.id) for identity in
                new_individual.identities]
            return success_response(
                "Individual created successfully.",
                {"individual": individual_out.model_dump()},
                201)
        except SQLAlchemyError as e:
            logger.error(f"Error creating individual: {e}")
            raise InternalServerError("Database error occurred.")


@api_individuals_bp.route("/", methods=["GET"])
@require_project_access
def list_individuals():
    """
    List all individuals within a specific project.
    Optional query parameter 'q' for search.
    """
    search_query = request.args.get("q", type=str, default=None)
    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        try:
            individuals = service_individual.get_individuals_by_project(
                user_id=g.user_id,
                project_id=g.project_id,
                search_query=search_query if search_query else None
            )
            individuals_out = []
            for individual in individuals:
                individual_out = IndividualOut.model_validate(
                    individual, from_attributes=True)
                individual_out.identities = [IdentityIdOut(id=i.id)
                                             for i in
                                             individual.identities]
                individuals_out.append(individual_out.model_dump())
            return success_response(
                "Individuals fetched successfully.",
                {"project_id": g.project_id,
                 "individuals": individuals_out})
        except SQLAlchemyError as e:
            logger.error(f"Error listing individuals: {e}")
            raise InternalServerError("Database error occurred.")


@api_individuals_bp.route("/<int:individual_id>", methods=["GET"])
@require_project_access
def get_individual(individual_id):
    """
    Retrieve detailed information of a specific individual by ID.
    """
    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        try:
            individual = service_individual.get_individual_by_id(
                individual_id=individual_id,
                user_id=g.user_id,
                project_id=g.project_id
            )
            if not individual:
                raise NotFound("Individual not found.")
            individual_out = IndividualOut.model_validate(individual,
                                                          from_attributes=True)
            individual_out.identities = [IdentityIdOut(id=i.id) for i
                                         in individual.identities]
            data = individual_out.model_dump()
            data["parents"] = individual.parents
            data["children"] = individual.children
            data["partners"] = individual.partners
            data["siblings"] = individual.siblings
            return success_response(
                "Individual fetched successfully.", {"data": data})
        except SQLAlchemyError as e:
            logger.error(f"Error fetching individual: {e}")
            raise InternalServerError("Database error occurred.")


@api_individuals_bp.route("/<int:individual_id>", methods=["PATCH"])
@require_project_access
def update_individual(individual_id):
    """
    Update an existing individual.
    Expects JSON payload conforming to IndividualUpdate schema.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("No input data provided.")
    try:
        individual_update = IndividualUpdate.model_validate(data)
    except ValidationError as e:
        raise BadRequest(str(e))

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        try:
            updated = service_individual.update_individual(
                individual_id=individual_id,
                user_id=g.user_id,
                project_id=g.project_id,
                individual_update=individual_update
            )
            if not updated:
                raise BadRequest("Failed to update individual.")
            individual_out = IndividualOut.model_validate(updated,
                                                          from_attributes=True)
            individual_out.identities = [
                IdentityIdOut(id=identity.id) for identity in
                updated.identities]
            return success_response(
                "Individual updated successfully.",
                {"data": individual_out.model_dump()})
        except SQLAlchemyError as e:
            logger.error(f"Error updating individual: {e}")
            raise InternalServerError("Database error occurred.")


@api_individuals_bp.route("/<int:individual_id>", methods=["DELETE"])
@require_project_access
def delete_individual(individual_id):
    """
    Delete an individual by their ID.
    """
    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        try:
            success = service_individual.delete_individual(
                individual_id,
                user_id=g.user_id,
                project_id=g.project_id
            )
            if success:
                return success_response(
                    "Individual deleted successfully.",
                    status_code=200)
            raise BadRequest("Failed to delete individual.")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting individual: {e}")
            raise InternalServerError("Database error occurred.")


@api_individuals_bp.route("/search", methods=["GET"])
@require_project_access
def search_individuals():
    """
    Search for individuals within a project based on a query.
    Optional query parameter 'exclude_ids' can be provided as a comma-separated string.
    """
    q = request.args.get("q", "", type=str)
    exclude_ids = request.args.get("exclude_ids", "", type=str)
    try:
        exclude_list = [int(x) for x in exclude_ids.split(",") if
                        x.strip()] if exclude_ids.strip() else []
    except ValueError:
        raise BadRequest("Invalid exclude_ids parameter.")

    with SessionLocal() as session:
        try:
            from app.services.project_service import ProjectService
            service_project = ProjectService(db=session)
            project = service_project.get_project_by_id(
                project_id=g.project_id)
            if not project or project.user_id != g.user_id:
                raise NotFound(
                    "Project not found or not owned by this user.")
            service_individual = IndividualService(db=session)
            individuals = service_individual.get_individuals_by_project(
                user_id=g.user_id,
                project_id=g.project_id,
                search_query=q if q else None
            )
            filtered = [i for i in individuals if
                        i.id not in exclude_list]
            results = []
            for i in filtered:
                out = IndividualOut.model_validate(i,
                                                   from_attributes=True)
                out.identities = [IdentityIdOut(id=ident.id) for
                                  ident in i.identities]
                results.append(out.model_dump())
            return success_response("Search completed.",
                                    {"individuals": results})
        except SQLAlchemyError as e:
            logger.error(f"Error searching individuals: {e}")
            raise InternalServerError("Database error occurred.")
