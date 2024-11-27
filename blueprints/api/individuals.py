from flask import Blueprint, jsonify, request
from flask_pydantic import validate
from models.individual import Individual
from models.identity import Identity
from schemas.subject_schema import (
    IndividualCreate,
    IndividualUpdate,
    IndividualOut,
    IdentityCreate,
    IdentityUpdate,
    IdentityOut
)
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

individuals_api_bp = Blueprint('individuals_api', __name__)


# Create Individual with Default Identity
@individuals_api_bp.route('/', methods=['POST'])
@jwt_required()
@validate()
def create_individual():
    data = request.get_json()
    body = IndividualCreate(**data)
    current_user_id = get_jwt_identity()

    # Step 1: Create the individual
    new_individual = Individual(
        user_id=current_user_id,
        birth_date=body.birth_date,
        birth_place=body.birth_place,
        death_date=body.death_date,
        death_place=body.death_place,
    )
    db.session.add(new_individual)
    db.session.flush()  # Ensure new_individual.id is available

    # Step 2: Create a default identity for the individual
    default_identity = Identity(
        individual_id=new_individual.id,
        first_name=body.first_name,  # Name fields from IndividualCreate
        last_name=body.last_name,
        gender=body.gender,
        valid_from=body.birth_date  # Start validity from birth date
    )
    db.session.add(default_identity)
    db.session.commit()

    individual_out = IndividualOut.from_orm(new_individual)
    return jsonify(individual_out.model_dump()), 201


# Get Individuals
@individuals_api_bp.route('/', methods=['GET'])
@jwt_required()
def get_individuals():
    current_user_id = get_jwt_identity()
    search_query = request.args.get('q')
    limit = request.args.get('limit', 10, type=int)

    query = Individual.query.filter_by(user_id=current_user_id)
    if search_query:
        query = query.filter(
            Individual.name.ilike(f"%{search_query}%") |
            Individual.birth_place.ilike(f"%{search_query}%")
        )

    individuals = query.order_by(Individual.updated_at.desc()).limit(limit).all()
    individuals_out = [
        IndividualOut.from_orm(individual).model_dump()
        for individual in individuals
    ]
    return jsonify(individuals_out), 200


# Get Individual by ID
@individuals_api_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_individual(id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()
    individual_out = IndividualOut.from_orm(individual)
    return jsonify(individual_out.model_dump()), 200


# Update Individual
@individuals_api_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@validate()
def update_individual(id: int):
    data = request.get_json()
    body = IndividualUpdate(**data)
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(individual, key, value)
    db.session.commit()

    individual_out = IndividualOut.from_orm(individual)
    return jsonify(individual_out.model_dump()), 200


# Delete Individual
@individuals_api_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_individual(id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=id, user_id=current_user_id).first_or_404()

    db.session.delete(individual)
    db.session.commit()
    return jsonify({'message': 'Individual deleted successfully'}), 200


# Add Identity
@individuals_api_bp.route('/<int:individual_id>/identities', methods=['POST'])
@jwt_required()
@validate()
def add_identity(individual_id: int):
    data = request.get_json()
    body = IdentityCreate(**data)
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id, user_id=current_user_id).first_or_404()

    new_identity = Identity(
        individual_id=individual_id,
        first_name=body.first_name,
        last_name=body.last_name,
        gender=body.gender,
        valid_from=body.valid_from,
        valid_until=body.valid_until,
    )
    db.session.add(new_identity)
    db.session.commit()

    identity_out = IdentityOut.from_orm(new_identity)
    return jsonify(identity_out.model_dump()), 201


# Update Identity
@individuals_api_bp.route('/<int:individual_id>/identities/<int:id>', methods=['PUT'])
@jwt_required()
@validate()
def update_identity(individual_id: int, id: int):
    data = request.get_json()
    body = IdentityUpdate(**data)
    current_user_id = get_jwt_identity()

    identity = Identity.query.join(Individual).filter(
        Identity.id == id,
        Individual.id == individual_id,
        Individual.user_id == current_user_id
    ).first_or_404()

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(identity, key, value)
    db.session.commit()

    identity_out = IdentityOut.from_orm(identity)
    return jsonify(identity_out.model_dump()), 200


# Delete Identity
@individuals_api_bp.route('/<int:individual_id>/identities/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_identity(individual_id: int, id: int):
    current_user_id = get_jwt_identity()

    identity = Identity.query.join(Individual).filter(
        Identity.id == id,
        Individual.id == individual_id,
        Individual.user_id == current_user_id
    ).first_or_404()

    db.session.delete(identity)
    db.session.commit()
    return jsonify({'message': 'Identity deleted successfully'}), 200
