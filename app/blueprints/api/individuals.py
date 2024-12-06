from flask import Blueprint, jsonify, request, current_app
from flask_pydantic import validate
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.individual import Individual
from app.models.identity import Identity
from app.schemas import (
    IndividualUpdate,
    IndividualOut
)
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

api_individuals_bp = Blueprint('api_individuals_bp', __name__)


# Utility Functions
def parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
    """Utility function to safely parse a date string."""
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_app.logger.error(
                f"Invalid date format: {date_str}")
    return None


def get_individual_or_404(individual_id: int,
                          user_id: int) -> Individual:
    """Helper function to get an individual by ID and user ID."""
    return Individual.query.filter_by(id=individual_id,
                                      user_id=user_id).first_or_404()


def format_individual_response(individual: Individual) -> dict:
    """Helper function to format an individual for JSON response."""
    primary_identity = individual.primary_identity
    name = f"{primary_identity.first_name} {primary_identity.last_name}" if primary_identity else "Unknown"
    return {
        'id': individual.id,
        'name': name
    }


# Search Individuals
@api_individuals_bp.route('/search', methods=['GET'])
@jwt_required()
def search_individuals():
    """
    Searches individuals by name based on the query provided.
    Excludes a specific individual if 'exclude_id' is provided.
    """
    try:
        current_user_id = get_jwt_identity()
        search_query = request.args.get('q', '').strip()
        exclude_id = request.args.get('exclude_id', type=int)

        # Return empty if search query is too short
        if len(search_query) < 2:
            return jsonify({'individuals': []}), 200

        # Filter individuals by user ID and search query in first/last name
        query = Individual.query.filter(
            Individual.user_id == current_user_id
        ).join(Identity).filter(
            (Identity.first_name.ilike(f'%{search_query}%')) |
            (Identity.last_name.ilike(f'%{search_query}%'))
        )

        if exclude_id:
            query = query.filter(Individual.id != exclude_id)

        individuals = query.limit(10).all()
        result = [format_individual_response(ind) for ind in
                  individuals]

        return jsonify({'individuals': result}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error during individual search: {e}")
        return jsonify(
            {'error': 'Database error occurred during search'}), 500

    except Exception as e:
        current_app.logger.error(
            f"Unexpected error during search: {e}")
        return jsonify({
                           'error': 'Unexpected error occurred during search'}), 500


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
        create_identity(new_individual.id, body.first_name,
                        body.last_name, body.gender, body.birth_date)

        # Add additional identities if provided
        for identity_data in body.identities or []:
            create_identity(new_individual.id,
                            identity_data.first_name,
                            identity_data.last_name,
                            identity_data.gender,
                            identity_data.valid_from,
                            identity_data.valid_until)

        db.session.commit()
        return jsonify({
            'message': 'Individual created successfully.',
            'data': IndividualOut.from_orm(
                new_individual).model_dump()
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating individual: {e}")
        return jsonify({
            'error': 'A database error occurred while creating the individual.'}), 500

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred while creating the individual.'}), 500


def create_identity(individual_id: int, first_name: str,
                    last_name: str, gender: str,
                    valid_from: Optional[str] = None,
                    valid_until: Optional[str] = None):
    """Helper function to create and add an identity to an individual."""
    new_identity = Identity(
        individual_id=individual_id,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        valid_from=parse_date(valid_from),
        valid_until=parse_date(valid_until)
    )
    db.session.add(new_identity)


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
        search_query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)

        query = Individual.query.filter_by(user_id=current_user_id)
        if search_query:
            query = query.join(Identity, isouter=True).filter(
                (Identity.first_name.ilike(f'%{search_query}%')) |
                (Identity.last_name.ilike(f'%{search_query}%')) |
                (Individual.birth_place.ilike(f'%{search_query}%'))
            )

        individuals = query.order_by(
            Individual.updated_at.desc()).limit(limit).all()

        data = [format_individual_response(ind) for ind in
                individuals]

        return jsonify({
            'message': 'Individuals retrieved successfully.',
            'data': data
        }), 200 if individuals else 404

    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error retrieving individuals: {e}")
        return jsonify({
            'error': 'A database error occurred while retrieving individuals.'}), 500

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {e}")
        return jsonify({
            'error': 'An unexpected error occurred while retrieving individuals.'}), 500
