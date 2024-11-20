from flask import Blueprint, request, jsonify
from models import Identity, Individual
from schemas.identity_schema import IdentitySchema
from extensions import db

identities_bp = Blueprint('individuals_identities', __name__, url_prefix='/individuals/<int:individual_id>/identities')

# Marshmallow schema
identity_schema = IdentitySchema()
identities_schema = IdentitySchema(many=True)

# Add Identity
@identities_bp.route('', methods=['POST'])
def add_identity(individual_id):
    data = request.json
    individual = Individual.query.get_or_404(individual_id)

    try:
        identity = identity_schema.load(data)
        identity.individual = individual
        db.session.add(identity)
        db.session.commit()
        return jsonify({'message': 'Identity added successfully', 'id': identity.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Update Identity
@identities_bp.route('/<int:id>', methods=['PUT'])
def update_identity(individual_id, id):
    identity = Identity.query.get_or_404(id)
    data = request.json

    try:
        for key, value in data.items():
            setattr(identity, key, value)
        db.session.commit()
        return jsonify({'message': 'Identity updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Delete Identity
@identities_bp.route('/<int:id>', methods=['DELETE'])
def delete_identity(individual_id, id):
    identity = Identity.query.get_or_404(id)
    db.session.delete(identity)
    db.session.commit()
    return jsonify({'message': 'Identity deleted successfully'}), 200
