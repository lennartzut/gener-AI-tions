from flask import Blueprint, jsonify
from flask_pydantic import validate
from models import Identity, Individual
from schemas.subject_schema import IdentityCreate, IdentityUpdate, \
    IdentityOut
from extensions import db

identities_bp = Blueprint('individuals_identities', __name__)


# Add Identity
@identities_bp.route('/<int:individual_id>/identities',
                     methods=['POST'])
@validate()
def add_identity(individual_id: int, body: IdentityCreate):
    individual = Individual.query.get_or_404(individual_id)
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
@identities_bp.route('/<int:individual_id>/identities/<int:id>',
                     methods=['PUT'])
@validate()
def update_identity(individual_id: int, id: int,
                    body: IdentityUpdate):
    identity = Identity.query.get_or_404(id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(identity, key, value)
    db.session.commit()
    identity_out = IdentityOut.from_orm(identity)
    return jsonify(identity_out.model_dump()), 200


# Delete Identity
@identities_bp.route('/<int:individual_id>/identities/<int:id>',
                     methods=['DELETE'])
def delete_identity(individual_id: int, id: int):
    identity = Identity.query.get_or_404(id)
    db.session.delete(identity)
    db.session.commit()
    return jsonify({'message': 'Identity deleted successfully'}), 200
