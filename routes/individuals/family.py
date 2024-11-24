from flask import Blueprint, jsonify
from flask_pydantic import validate
from models import Individual, Relationship, Family
from schemas.subject_schema import IndividualOut, IdentityOut
from schemas.relationship_schema import RelationshipRequest
from extensions import db

family_bp = Blueprint('individuals_family', __name__)


# Family Card
@family_bp.route('/<int:id>/family-card', methods=['GET'])
def get_family_card(id: int):
    individual = Individual.query.get_or_404(id)
    data = {
        'individual': IndividualOut.from_orm(
            individual).model_dump(),
        'parents': [IndividualOut.from_orm(parent).model_dump() for
                    parent in individual.get_parents()],
        'siblings': [IndividualOut.from_orm(sibling).model_dump() for
                     sibling in individual.get_siblings()],
        'partners': [IndividualOut.from_orm(partner).model_dump() for
                     partner in individual.get_partners()],
        'children': [IndividualOut.from_orm(child).model_dump() for
                     child in individual.get_children()],
        'identities': [IdentityOut.from_orm(identity).model_dump()
                       for identity in individual.identities],
    }
    return jsonify(data), 200


# Add Relationship
@family_bp.route('/<int:id>/add-relationship', methods=['POST'])
@validate()
def add_relationship(id: int, body: RelationshipRequest):
    relationship_type = body.type
    target_id = body.target_id

    if relationship_type == 'parent':
        relationship = Relationship(
            parent_id=target_id,
            related_individual_id=id,
            relationship_type='parent'
        )
    elif relationship_type == 'child':
        relationship = Relationship(
            parent_id=id,
            related_individual_id=target_id,
            relationship_type='child'
        )
    elif relationship_type == 'partner':
        relationship = Family(partner1_id=id, partner2_id=target_id)
        db.session.add(relationship)
        db.session.commit()
        return jsonify({
                           'message': 'Family relationship added successfully'}), 201
    else:
        return jsonify({'error': 'Invalid relationship type'}), 400

    db.session.add(relationship)
    db.session.commit()
    return jsonify(
        {'message': 'Relationship added successfully'}), 201
