import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from app.extensions import SessionLocal
from app.schemas.individual_schema import IndividualCreate, IndividualUpdate, IndividualOut
from app.schemas.identity_schema import IdentityOut
from app.services.individual_service import IndividualService
from app.services.project_service import ProjectService
from app.utils.auth_utils import validate_token_and_get_user

logger = logging.getLogger(__name__)

api_individuals_bp = Blueprint('api_individuals_bp', __name__)


@api_individuals_bp.route('/search', methods=['GET'])
@jwt_required()
def search_individuals():
    """
    Search individuals in a project.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    q = request.args.get('q', '', type=str)
    exclude_ids = request.args.get('exclude_ids', '', type=str)
    try:
        exclude_list = [int(x) for x in exclude_ids.split(',') if x.strip()] if exclude_ids.strip() else []
    except ValueError:
        return jsonify({"error": "Invalid exclude_ids parameter."}), 400

    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        service_individual = IndividualService(db=session)

        project = service_project.get_project_by_id(project_id=project_id)
        if not project or project.user_id != user_id:
            return jsonify({"error": "Project not found or not owned by this user."}), 404

        individuals = service_individual.get_individuals_by_project(
            user_id=user_id,
            project_id=project_id,
            search_query=q if q else None
        )
        individuals = [i for i in individuals if i.id not in exclude_list]

        individuals_out = []
        for individual in individuals:
            individual_data = IndividualOut.from_orm(individual).dict()
            individual_data['identities'] = [
                IdentityOut.from_orm(identity).model_dump() for identity in individual.identities
            ]
            individuals_out.append(individual_data)

    return jsonify({"individuals": individuals_out}), 200


@api_individuals_bp.route('/', methods=['GET'])
@jwt_required()
def list_individuals():
    """
    List all individuals in a specific project.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    search_query = request.args.get('q', type=str, default=None)

    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        service_individual = IndividualService(db=session)

        project = service_project.get_project_by_id(project_id=project_id)
        if not project or project.user_id != user_id:
            return jsonify({"error": "Project not found or not owned by the user."}), 404

        individuals = service_individual.get_individuals_by_project(
            user_id=user_id,
            project_id=project_id,
            search_query=search_query
        )

        individuals_out = []
        for individual in individuals:
            individual_out = IndividualOut.from_orm(individual)
            individual_out.identities = [
                IdentityOut.from_orm(identity) for identity in
                individual.identities
            ]
            individuals_out.append(individual_out.model_dump())

    return jsonify({"project_id": project_id, "individuals": individuals_out}), 200


@api_individuals_bp.route('/', methods=['POST'])
@jwt_required()
def create_individual():
    """
    Create a new individual within a project.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided."}), 400

    try:
        individual_create = IndividualCreate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        new_individual = service_individual.create_individual(
            user_id=user_id,
            project_id=project_id,
            individual_create=individual_create
        )
        if new_individual:
            return jsonify({
                "message": "Individual created successfully.",
                "data": IndividualOut.from_orm(new_individual).model_dump()
            }), 201
        return jsonify({"error": "Failed to create individual."}), 400


@api_individuals_bp.route('/<int:individual_id>', methods=['GET'])
@jwt_required()
def get_individual(individual_id):
    """
    Retrieve details of an individual by ID.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        individual = service_individual.get_individual_by_id(
            individual_id=individual_id,
            user_id=user_id,
            project_id=project_id
        )
        if individual:
            individual_data = IndividualOut.from_orm(individual).dict()
            individual_data['identities'] = [
                IdentityOut.from_orm(identity).model_dump() for identity in individual.identities
            ]
            return jsonify({"data": individual_data}), 200
        return jsonify({"error": "Individual not found."}), 404


@api_individuals_bp.route('/<int:individual_id>', methods=['PATCH'])
@jwt_required()
def update_individual(individual_id):
    """
    Update an individual's details.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided."}), 400

    try:
        individual_update = IndividualUpdate.model_validate(data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        updated_individual = service_individual.update_individual(
            individual_id=individual_id,
            user_id=user_id,
            project_id=project_id,
            individual_update=individual_update
        )
        if updated_individual:
            return jsonify({
                "message": "Individual updated successfully.",
                "data": IndividualOut.from_orm(updated_individual).model_dump()
            }), 200
        return jsonify({"error": "Failed to update individual."}), 400


@api_individuals_bp.route('/<int:individual_id>', methods=['DELETE'])
@jwt_required()
def delete_individual(individual_id):
    """
    Delete an individual by ID.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        if service_individual.delete_individual(
                individual_id=individual_id, user_id=user_id, project_id=project_id):
            return jsonify({"message": "Individual deleted successfully."}), 200
        return jsonify({"error": "Failed to delete individual."}), 400
