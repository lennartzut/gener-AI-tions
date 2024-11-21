from flask import Blueprint, request, jsonify
from models import Individual, Relationship, Family
from schemas.individual_schema import IndividualSchema
from schemas.identity_schema import IdentitySchema
from extensions import db

family_bp = Blueprint('individuals_family', __name__,
                      url_prefix='/individuals')

# Marshmallow schemas
individual_schema = IndividualSchema()
identity_schema = IdentitySchema()


# Family Card
@family_bp.route('/<int:id>/family-card', methods=['GET'])
def get_family_card(id):
    individual = Individual.query.get_or_404(id)
    data = {
        'individual': individual_schema.dump(individual),
        'parents': individual_schema.dump(individual.get_parents(),
                                          many=True),
        'siblings': individual_schema.dump(individual.get_siblings(),
                                           many=True),
        'partners': individual_schema.dump(individual.get_partners(),
                                           many=True),
        'children': individual_schema.dump(individual.get_children(),
                                           many=True),
        'identities': identity_schema.dump(individual.identities,
                                           many=True),
    }
    return jsonify(data), 200


# Add Relationship
@family_bp.route('/<int:id>/add-relationship', methods=['POST'])
def add_relationship(id):
    data = request.json
    relationship_type = data.get(
        'type')  # e.g., 'parent', 'child', 'partner'
    target_id = data.get('target_id')

    if relationship_type == 'parent':
        relationship = Relationship(parent_id=target_id, related_individual_id=id)
    elif relationship_type == 'child':
        relationship = Relationship(parent_id=id, related_individual_id=target_id)
    elif relationship_type == 'partner':
        relationship = Family(partner1_id=id, partner2_id=target_id)
    else:
        return jsonify({'error': 'Invalid relationship type'}), 400

    db.session.add(relationship)
    db.session.commit()
    return jsonify(
        {'message': 'Relationship added successfully'}), 201
