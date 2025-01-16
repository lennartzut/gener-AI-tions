import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.extensions import SessionLocal
from app.schemas.identity_schema import IdentityIdOut
from app.schemas.individual_schema import IndividualCreate, \
    IndividualUpdate, IndividualOut
from app.services.individual_service import IndividualService
from app.services.project_service import ProjectService
from app.utils.auth import validate_token_and_get_user
from app.utils.project import get_project_or_404

logger = logging.getLogger(__name__)

api_individuals_bp = Blueprint("api_individuals_bp", __name__)


@api_individuals_bp.route("/", methods=["POST"])
@jwt_required()
def create_individual():
    """
    Create a new individual within a project.

    Query Parameters:
        project_id (int): The ID of the project.

    Expects:
        JSON payload conforming to the IndividualCreate schema.

    Returns:
        JSON response with a success message and the created individual data or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "No input data provided."}), 400

    individual_create = IndividualCreate.model_validate(data)

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        new_individual = service_individual.create_individual(
            user_id=user_id,
            project_id=project_id,
            individual_create=individual_create
        )
        if not new_individual:
            return jsonify(
                {"error": "Failed to create individual."}), 400

        individual_out = IndividualOut.model_validate(new_individual,
                                                      from_attributes=True)
        individual_out.identities = [IdentityIdOut(id=identity.id)
                                     for identity in
                                     new_individual.identities]

        return jsonify({
            "message": "Individual created successfully.",
            "data": individual_out.model_dump()
        }), 201


@api_individuals_bp.route("/", methods=["GET"])
@jwt_required()
def list_individuals():
    """
    List all individuals within a specific project.

    Query Parameters:
        project_id (int): The ID of the project.
        q (str, optional): Search query to filter individuals by name or birth place.

    Returns:
        JSON response containing a list of individuals or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    search_query = request.args.get("q", type=str, default=None)

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        individuals = service_individual.get_individuals_by_project(
            user_id=user_id,
            project_id=project_id,
            search_query=search_query
        )

        individuals_out = []
        for ind in individuals:
            individual_out = IndividualOut.model_validate(ind,
                                                          from_attributes=True)
            individuals_out.append(individual_out.model_dump())

    return jsonify({
        "project_id": project_id,
        "individuals": individuals_out
    }), 200


@api_individuals_bp.route("/<int:individual_id>", methods=["GET"])
@jwt_required()
def get_individual(individual_id):
    """
    Retrieve detailed information of a specific individual by ID.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        individual_id (int): The unique ID of the individual.

    Returns:
        JSON response containing the individual's details, including related individuals,
        or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        individual = service_individual.get_individual_by_id(
            individual_id=individual_id,
            user_id=user_id,
            project_id=project_id
        )
        if not individual:
            return jsonify({"error": "Individual not found."}), 404

        # Convert to our IndividualOut schema
        individual_out = IndividualOut.model_validate(
            individual, from_attributes=True
        )
        # Only basic identity IDs here (the actual data is in primary_identity)
        individual_out.identities = [{"id": identity.id} for identity in individual.identities]

        # Turn the Pydantic model into a dict
        data = individual_out.model_dump()

        # Now we simply copy from the model's canonical @property logic
        data["parents"] = individual.parents
        data["children"] = individual.children
        data["partners"] = individual.partners
        data["siblings"] = individual.siblings

    return jsonify({"data": data}), 200



@api_individuals_bp.route("/<int:individual_id>", methods=["PATCH"])
@jwt_required()
def update_individual(individual_id):
    """
    Update the details of an existing individual.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        individual_id (int): The unique ID of the individual to update.

    Expects:
        JSON payload conforming to the IndividualUpdate schema.

    Returns:
        JSON response with a success message and the updated individual data or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "No input data provided."}), 400

    try:
        ind_update = IndividualUpdate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        try:
            updated_individual = service_individual.update_individual(
                individual_id=individual_id,
                user_id=user_id,
                project_id=project_id,
                individual_update=ind_update
            )
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

        if updated_individual:
            individual_out = IndividualOut.model_validate(
                updated_individual, from_attributes=True)
            individual_out.identities = [
                IdentityIdOut(id=identity.id) for identity in
                updated_individual.identities]
            return jsonify({
                "message": "Individual updated successfully.",
                "data": individual_out.model_dump()
            }), 200

        return jsonify(
            {"error": "Failed to update individual."}), 400


@api_individuals_bp.route("/<int:individual_id>", methods=["DELETE"])
@jwt_required()
def delete_individual(individual_id):
    """
    Delete an individual by their ID.

    Query Parameters:
        project_id (int): The ID of the project.

    Args:
        individual_id (int): The unique ID of the individual to delete.

    Returns:
        JSON response with a success message or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        if service_individual.delete_individual(individual_id,
                                                user_id, project_id):
            return jsonify(
                {"message": "Individual deleted successfully."}), 200
        return jsonify(
            {"error": "Failed to delete individual."}), 400


@api_individuals_bp.route("/search", methods=["GET"])
@jwt_required()
def search_individuals():
    """
    Search for individuals within a project based on a query.

    Query Parameters:
        project_id (int): The ID of the project.
        q (str, optional): The search query.
        exclude_ids (str, optional): Comma-separated list of individual IDs to exclude.

    Returns:
        JSON response containing a list of matched individuals or error details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    q = request.args.get("q", "", type=str)
    exclude_ids = request.args.get("exclude_ids", "", type=str)
    try:
        exclude_list = [int(x) for x in exclude_ids.split(",") if
                        x.strip()] if exclude_ids.strip() else []
    except ValueError:
        return jsonify(
            {"error": "Invalid exclude_ids parameter."}), 400

    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        project = service_project.get_project_by_id(
            project_id=project_id)
        if not project or project.user_id != user_id:
            return jsonify({
                               "error": "Project not found or not owned by this user."}), 404

        service_individual = IndividualService(db=session)
        individuals = service_individual.get_individuals_by_project(
            user_id=user_id,
            project_id=project_id,
            search_query=q if q else None
        )
        # Exclude certain IDs
        individuals = [i for i in individuals if
                       i.id not in exclude_list]

        search_out = []
        for i in individuals:
            individual_out = IndividualOut.model_validate(i,
                                                          from_attributes=True)
            individual_out.identities = [identity.id for identity in
                                         i.identities]
            search_out.append(individual_out.model_dump())

    return jsonify({"individuals": search_out}), 200
