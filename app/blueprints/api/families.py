from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.individual import Individual
from app.models.relationship import Relationship
from app.extensions import db

api_families_bp = Blueprint('api_families_bp', __name__)


@api_families_bp.route('/<int:individual_id>', methods=['GET'])
@jwt_required()
def get_family_data(individual_id):
    """
    Retrieves family data for a given individual, including parents,
    siblings, partners, and children.
    """
    try:
        current_user_id = get_jwt_identity()

        # Fetch the individual belonging to the logged-in user
        individual = Individual.query.filter_by(
            id=individual_id, user_id=current_user_id
        ).first_or_404()

        # Prepare family data
        family_data = {
            'individual': individual.to_dict(),
            'parents': [parent.to_dict() for parent in
                        individual.get_parents()],
            'siblings': [sibling.to_dict() for sibling in
                         individual.get_siblings()],
            'partners': [partner.to_dict() for partner in
                         individual.get_partners()],
            'children': [child.to_dict() for child in
                         individual.get_children()],
        }

        return jsonify({
            'message': 'Family data retrieved successfully',
            'data': family_data
        }), 200

    except Exception as e:
        current_app.logger.error(
            f"Error retrieving family data for individual {individual_id}: {e}")
        return jsonify({
                           'error': 'An error occurred while retrieving family data.'}), 500


@api_families_bp.route('/<int:individual_id>/relationships',
                       methods=['POST'])
@jwt_required()
def add_relationship(individual_id):
    """
    Adds a relationship between the given individual and another individual
    as either a parent or a child.
    """
    try:
        current_user_id = get_jwt_identity()

        # Fetch the individual belonging to the logged-in user
        individual = Individual.query.filter_by(
            id=individual_id, user_id=current_user_id
        ).first_or_404()

        # Parse request data
        data = request.get_json()
        relationship_type = data.get('type')
        target_id = data.get('target_id')

        # Validate input
        if not relationship_type or not target_id:
            return jsonify({
                               'error': 'Relationship type and target individual are required.'}), 400

        if relationship_type not in ['parent', 'child']:
            return jsonify({
                               'error': 'Invalid relationship type. Must be either "parent" or "child".'}), 400

        # Fetch the target individual
        target_individual = Individual.query.filter_by(
            id=target_id, user_id=current_user_id
        ).first_or_404()

        # Initialize the relationship variable
        relationship = None

        # Create the relationship based on the specified type
        if relationship_type == 'parent':
            relationship = Relationship(
                parent_id=target_individual.id,
                child_id=individual.id
            )
        elif relationship_type == 'child':
            relationship = Relationship(
                parent_id=individual.id,
                child_id=target_individual.id
            )

        # Ensure relationship was created successfully
        if relationship is None:
            return jsonify(
                {'error': 'Failed to create relationship.'}), 400

        # Commit the new relationship
        db.session.add(relationship)
        db.session.commit()

        return jsonify(
            {'message': 'Relationship added successfully.'}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error adding relationship for individual {individual_id}: {e}")
        return jsonify({
                           'error': 'An error occurred while adding the relationship.'}), 500
