from flask import Blueprint, jsonify, request, current_app
from flask_pydantic import validate
from flask_jwt_extended import jwt_required, get_jwt_identity
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
from datetime import datetime

api_individuals_bp = Blueprint('api_individuals_bp', __name__)


def parse_date(date_str):
    """
    Utility function to safely parse a date string.
    """
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_app.logger.error(
                f"Invalid date format: {date_str}")
            return None
    return None


# Create Individual with Default Identity
@api_individuals_bp.route('/', methods=['POST'],
                          strict_slashes=False)
@jwt_required()
@validate(body=IndividualUpdate)
def create_individual(body: IndividualUpdate):
    """
    Creates a new individual along with their default identity.
    """
    current_user_id = get_jwt_identity()

    try:
        # Create the individual
        new_individual = Individual(
            user_id=current_user_id,
            birth_date=parse_date(body.birth_date),
            birth_place=body.birth_place,
            death_date=parse_date(body.death_date),
            death_place=body.death_place
        )
        db.session.add(new_individual)
        db.session.flush()  # Ensure new_individual.id is available

        # Create default identity
        default_identity = Identity(
            individual_id=new_individual.id,
            first_name=body.first_name,
            last_name=body.last_name,
            gender=body.gender,
            valid_from=parse_date(body.birth_date)
        )
        db.session.add(default_identity)

        # Add additional identities if provided
        for identity_data in body.identities or []:
            additional_identity = Identity(
                individual_id=new_individual.id,
                first_name=identity_data.first_name,
                last_name=identity_data.last_name,
                gender=identity_data.gender,
                valid_from=parse_date(identity_data.valid_from),
                valid_until=parse_date(identity_data.valid_until)
            )
            db.session.add(additional_identity)

        db.session.commit()
        return jsonify({
            'message': 'Individual created successfully.',
            'data': IndividualOut.from_orm(
                new_individual).model_dump()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating individual: {e}")
        return jsonify({
                           'error': 'An error occurred while creating the individual.'}), 500


# Get All Individuals
@api_individuals_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_individuals():
    """
    Retrieves a list of individuals belonging to the current user.
    Supports optional search and limit parameters.
    """
    try:
        current_user_id = get_jwt_identity()
        search_query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)

        query = Individual.query.filter_by(user_id=current_user_id)
        if search_query:
            query = query.join(Identity).filter(
                (Identity.first_name.ilike(f'%{search_query}%')) |
                (Identity.last_name.ilike(f'%{search_query}%')) |
                (Individual.birth_place.ilike(f'%{search_query}%'))
            )

        individuals = query.order_by(
            Individual.updated_at.desc()).limit(limit).all()
        return jsonify({
            'message': 'Individuals retrieved successfully.',
            'data': [IndividualOut.from_orm(ind).model_dump() for ind
                     in individuals]
        }), 200

    except Exception as e:
        current_app.logger.error(
            f"Error retrieving individuals: {e}")
        return jsonify({
                           'error': 'An error occurred while retrieving individuals.'}), 500


# Get Individual by ID
@api_individuals_bp.route('/<int:individual_id>', methods=['GET'],
                          strict_slashes=False)
@jwt_required()
def get_individual(individual_id):
    """
    Retrieves details of a specific individual by ID.
    """
    try:
        current_user_id = get_jwt_identity()
        individual = Individual.query.filter_by(id=individual_id,
                                                user_id=current_user_id).first_or_404()

        return jsonify({
            'message': 'Individual retrieved successfully.',
            'data': IndividualOut.from_orm(individual).model_dump()
        }), 200

    except Exception as e:
        current_app.logger.error(
            f"Error retrieving individual {individual_id}: {e}")
        return jsonify({
                           'error': 'An error occurred while retrieving the individual.'}), 500


# Update Individual
@api_individuals_bp.route('/<int:individual_id>', methods=['PUT'],
                          strict_slashes=False)
@jwt_required()
@validate()
def update_individual(individual_id, body: IndividualUpdate):
    """
    Updates an existing individual's details.
    """
    try:
        current_user_id = get_jwt_identity()
        individual = Individual.query.filter_by(id=individual_id,
                                                user_id=current_user_id).first_or_404()

        for key, value in body.model_dump(
                exclude_unset=True).items():
            setattr(individual, key, value)

        db.session.commit()
        return jsonify({
            'message': 'Individual updated successfully.',
            'data': IndividualOut.from_orm(individual).model_dump()
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error updating individual {individual_id}: {e}")
        return jsonify({
                           'error': 'An error occurred while updating the individual.'}), 500


# Delete Individual
@api_individuals_bp.route('/<int:individual_id>', methods=['DELETE'],
                          strict_slashes=False)
@jwt_required()
def delete_individual(individual_id):
    """
    Deletes an individual by ID.
    """
    try:
        current_user_id = get_jwt_identity()
        individual = Individual.query.filter_by(id=individual_id,
                                                user_id=current_user_id).first_or_404()

        db.session.delete(individual)
        db.session.commit()
        return jsonify(
            {'message': 'Individual deleted successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error deleting individual {individual_id}: {e}")
        return jsonify({
                           'error': 'An error occurred while deleting the individual.'}), 500


# Add Identity
@api_individuals_bp.route('/<int:individual_id>/identities',
                          methods=['POST'], strict_slashes=False)
@jwt_required()
@validate()
def add_identity(individual_id, body: IdentityCreate):
    """
    Adds a new identity for an individual.
    """
    try:
        current_user_id = get_jwt_identity()
        Individual.query.filter_by(id=individual_id,
                                   user_id=current_user_id).first_or_404()

        new_identity = Identity(
            individual_id=individual_id,
            first_name=body.first_name,
            last_name=body.last_name,
            gender=body.gender,
            valid_from=body.valid_from,
            valid_until=body.valid_until
        )
        db.session.add(new_identity)
        db.session.commit()
        return jsonify({
            'message': 'Identity added successfully.',
            'data': IdentityOut.from_orm(new_identity).model_dump()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error adding identity to individual {individual_id}: {e}")
        return jsonify({
                           'error': 'An error occurred while adding the identity.'}), 500
