import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.extensions import SessionLocal
from app.schemas.individual_schema import IndividualCreate, IndividualUpdate, IndividualOut
from app.schemas.identity_schema import IdentityIdOut
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
            return jsonify({"error": "Failed to create individual."}), 400

        individual_out = IndividualOut.model_validate(
            new_individual, from_attributes=True)
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
    List all individuals in a specific project, WITHOUT relationships attached.
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
            individual_out = IndividualOut.model_validate(
                ind,
                from_attributes=True
            )
            individuals_out.append(individual_out.model_dump())

    return jsonify({
        "project_id": project_id,
        "individuals": individuals_out
    }), 200


@api_individuals_bp.route("/<int:individual_id>", methods=["GET"])
@jwt_required()
def get_individual(individual_id):
    """
    Retrieve details of an individual by ID, including:
      - Full details for THIS individual
      - Short references (id, first_name, last_name, relationship_id)
        for parents/siblings/partners/children
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

        individual_out = IndividualOut.model_validate(
            individual,
            from_attributes=True
        )
        individual_out.identities = [{"id": identity.id} for identity
                                      in individual.identities]

        individual_data = individual_out.model_dump()

        individual_data["parents"] = [
            {
                "id": p.related.id,
                "first_name": p.related.primary_identity.first_name if p.related.primary_identity else None,
                "last_name": p.related.primary_identity.last_name if p.related.primary_identity else None,
                "relationship_id": p.id
            }
            for p in individual.relationships_as_individual
            if p.related and p.initial_relationship == "child"
        ]

        individual_data["children"] = [
            {
                "id": c.related.id,
                "first_name": c.related.primary_identity.first_name if c.related.primary_identity else None,
                "last_name": c.related.primary_identity.last_name if c.related.primary_identity else None,
                "relationship_id": c.id
            }
            for c in individual.relationships_as_individual
            if c.related and c.initial_relationship == "parent"
        ]

        individual_data["partners"] = [
            {
                "id": prt.related.id,
                "first_name": prt.related.primary_identity.first_name if prt.related.primary_identity else None,
                "last_name": prt.related.primary_identity.last_name if prt.related.primary_identity else None,
                "relationship_id": prt.id
            }
            for prt in individual.relationships_as_individual
            if prt.related and prt.initial_relationship == "partner"
        ]

        individual_data["siblings"] = [
            {
                "id": s.related.id,
                "first_name": s.related.primary_identity.first_name if s.related.primary_identity else None,
                "last_name": s.related.primary_identity.last_name if s.related.primary_identity else None
            }
            for s in individual.relationships_as_individual
            if s.related and s.initial_relationship == "sibling"
        ]

    return jsonify({"data": individual_data}), 200


@api_individuals_bp.route("/<int:individual_id>", methods=["PATCH"])
@jwt_required()
def update_individual(individual_id):
    """
    Update an individual's details.
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

    with (SessionLocal() as session):
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
            individual_out.identities = [IdentityIdOut(
                id=identity.id) for identity in
                updated_individual.identities]
            return jsonify({
                "message": "Individual updated successfully.",
                "data": individual_out.model_dump()
            }), 200

        return jsonify({"error": "Failed to update individual."}), 400


@api_individuals_bp.route("/<int:individual_id>", methods=["DELETE"])
@jwt_required()
def delete_individual(individual_id):
    """
    Delete an individual by ID.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    with SessionLocal() as session:
        service_individual = IndividualService(db=session)
        if service_individual.delete_individual(individual_id,
                                              user_id,
                                      project_id):
            return jsonify({"message": "Individual deleted successfully."}), 200
        return jsonify({"error": "Failed to delete individual."}), 400


@api_individuals_bp.route("/search", methods=["GET"])
@jwt_required()
def search_individuals():
    """
    Search individuals in a project.
    """
    user_id = validate_token_and_get_user()
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "Project ID is required."}), 400

    get_project_or_404(user_id=user_id, project_id=project_id)

    q = request.args.get("q", "", type=str)
    exclude_ids = request.args.get("exclude_ids", "", type=str)
    try:
        exclude_list = [int(x) for x in exclude_ids.split(",") if x.strip()] if exclude_ids.strip() else []
    except ValueError:
        return jsonify({"error": "Invalid exclude_ids parameter."}), 400

    with SessionLocal() as session:
        service_project = ProjectService(db=session)
        project = service_project.get_project_by_id(project_id=project_id)
        if not project or project.user_id != user_id:
            return jsonify({"error": "Project not found or not owned by this user."}), 404

        service_individual = IndividualService(db=session)
        individuals = service_individual.get_individuals_by_project(
            user_id=user_id,
            project_id=project_id,
            search_query=q if q else None
        )
        # exclude certain IDs
        individuals = [i for i in individuals if i.id not in exclude_list]

        search_out = []
        for i in individuals:
            individual_out = IndividualOut.model_validate(i, from_attributes=True)
            individual_out.identities = [identity.id for identity in i.identities]
            search_out.append(individual_out.model_dump())

    return jsonify({"individuals": search_out}), 200
