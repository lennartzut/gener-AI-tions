from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.individual import Individual
from app.models.relationship import Relationship
from app.extensions import db

api_families_bp = Blueprint('api_families_bp', __name__)


# Get Family Data
@api_families_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_family_data(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()

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
    return jsonify(family_data), 200


# Add Relationship
@api_families_bp.route('/<int:id>/relationships', methods=['POST'])
@jwt_required()
def add_relationship(individual_id):
    current_user_id = get_jwt_identity()
    individual = Individual.query.filter_by(id=individual_id,
                                            user_id=current_user_id).first_or_404()
    data = request.get_json()

    relationship_type = data.get('type')
    target_id = data.get('target_id')

    if not relationship_type or not target_id:
        return jsonify({
            'error': 'Relationship type and target individual are required.'
        }), 400

    target_individual = Individual.query.filter_by(id=target_id,
                                                   user_id=current_user_id).first()
    if not target_individual:
        return jsonify(
            {'error': 'Target individual not found.'}), 404

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
    else:
        return jsonify({'error': 'Invalid relationship type.'}), 400

    db.session.add(relationship)
    db.session.commit()
    return jsonify(
        {'message': 'Relationship added successfully.'}), 201
