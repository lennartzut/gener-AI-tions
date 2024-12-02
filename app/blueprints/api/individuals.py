from flask import Blueprint, jsonify, request, current_app as app
from flask_pydantic import validate
from app.models.individual import Individual
from app.models.identity import Identity
from app.schemas import (
    IndividualUpdate,
    IndividualOut,
    IdentityCreate,
    IdentityUpdate,
    IdentityOut
)
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

api_individuals_bp = Blueprint('api_individuals_bp', __name__)


def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None
    return None


# Create Individual with Default Identity
@api_individuals_bp.route('/', methods=['POST'],
                          strict_slashes=False)
@jwt_required()
def create_individual():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    gender = data.get('gender')

    if not first_name or not last_name or not gender:
        return jsonify({
                           'error': 'First name, last name, and gender are required.'}), 400

    try:
        # Parse dates
        birth_date = parse_date(data.get('birth_date'))
        death_date = parse_date(data.get('death_date'))

        # Create the individual
        new_individual = Individual(
            user_id=current_user_id,
            birth_date=birth_date,
            birth_place=data.get('birth_place'),
            death_date=death_date,
            death_place=data.get('death_place'),
        )
        db.session.add(new_individual)
        db.session.flush()  # Ensure new_individual.id is available

        # Create default identity
        default_identity = Identity(
            individual_id=new_individual.id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            valid_from=birth_date
        )
        db.session.add(default_identity)

        # Process additional identities if any
        identities_data = data.get('identities', [])
        for identity_data in identities_data:
            # Parse identity dates
            valid_from = parse_date(identity_data.get('valid_from'))
            valid_until = parse_date(
                identity_data.get('valid_until'))

            # Validate and create additional identities
            new_identity = Identity(
                individual_id=new_individual.id,
                first_name=identity_data.get('first_name'),
                last_name=identity_data.get('last_name'),
                gender=identity_data.get('gender'),
                valid_from=valid_from,
                valid_until=valid_until,
            )
            db.session.add(new_identity)

        db.session.commit()

        # Return a simplified response
        return jsonify({
            'id': new_individual.id,
            'name': f"{default_identity.first_name} {default_identity.last_name}"
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating individual: {e}")
        return jsonify({
                           'error': 'An error occurred while creating the individual.'}), 500


# Get Individuals
@api_individuals_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_individuals():
    current_user_id = get_jwt_identity()
    search_query = request.args.get('q')
    limit = request.args.get('limit', 10, type=int)

    query = Individual.query.filter_by(user_id=current_user_id)
    if search_query:
        # Join with Identity model for searching by name
        query = query.join(Identity).filter(
            (Individual.birth_place.ilike(f"%{search_query}%")) |
            (Identity.first_name.ilike(f"%{search_query}%")) |
            (Identity.last_name.ilike(f"%{search_query}%"))
        )

    individuals = query.order_by(Individual.updated_at.desc()).limit(
        limit).all()
    individuals_out = [
        IndividualOut.from_orm(individual).model_dump()
        for individual in individuals
    ]
    return jsonify(individuals_out), 200


# Get Individual by ID
@api_individuals_bp.route('/<int:individual_id>', methods=['GET'],
                          strict_slashes=False)
@jwt_required()
def get_individual(individual_id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()
    individual_out = IndividualOut.from_orm(individual)
    return jsonify(individual_out.model_dump()), 200


# Update Individual
@api_individuals_bp.route('/<int:individual_id>', methods=['PUT'],
                          strict_slashes=False)
@jwt_required()
@validate()
def update_individual(individual_id: int, body: IndividualUpdate):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(individual, key, value)
    db.session.commit()

    individual_out = IndividualOut.from_orm(individual)
    return jsonify(individual_out.model_dump()), 200


# Delete Individual
@api_individuals_bp.route('/<int:individual_id>', methods=['DELETE'],
                          strict_slashes=False)
@jwt_required()
def delete_individual(individual_id: int):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

    db.session.delete(individual)
    db.session.commit()
    return jsonify(
        {'message': 'Individual deleted successfully'}), 200


# Add Identity
@api_individuals_bp.route('/<int:individual_id>/identities',
                          methods=['POST'], strict_slashes=False)
@jwt_required()
@validate()
def add_identity(individual_id: int, body: IdentityCreate):
    current_user_id = get_jwt_identity()
    # Verify that the individual exists and belongs to the current user
    _ = Individual.query.filter_by(id=individual_id,
                                   user_id=current_user_id).first_or_404()

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
@api_individuals_bp.route(
    '/<int:individual_id>/identities/<int:identity_id>',
    methods=['PUT'], strict_slashes=False)
@jwt_required()
@validate()
def update_identity(individual_id: int, identity_id: int,
                    body: IdentityUpdate):
    current_user_id = get_jwt_identity()

    identity = Identity.query.join(Individual).filter(
        Identity.id == identity_id,
        Individual.id == individual_id,
        Individual.user_id == current_user_id
    ).first_or_404()

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(identity, key, value)
    db.session.commit()

    identity_out = IdentityOut.from_orm(identity)
    return jsonify(identity_out.model_dump()), 200


# Delete Identity
@api_individuals_bp.route(
    '/<int:individual_id>/identities/<int:identity_id>',
    methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_identity(individual_id: int, identity_id: int):
    current_user_id = get_jwt_identity()

    identity = Identity.query.join(Individual).filter(
        Identity.id == identity_id,
        Individual.id == individual_id,
        Individual.user_id == current_user_id
    ).first_or_404()

    db.session.delete(identity)
    db.session.commit()
    return jsonify({'message': 'Identity deleted successfully'}), 200
