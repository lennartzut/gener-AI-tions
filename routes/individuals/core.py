from flask import Blueprint, jsonify
from flask_pydantic import validate
from models import Individual
from extensions import db
from schemas.subject_schema import (
    IndividualCreate,
    IndividualUpdate,
    IndividualOut,
)

core_bp = Blueprint('individuals_core', __name__)


# Create Individual
@core_bp.route('/', methods=['POST'])
@validate()
def create_individual(body: IndividualCreate):
    new_individual = Individual(
        birth_date=body.birth_date,
        birth_place=body.birth_place,
        death_date=body.death_date,
        death_place=body.death_place,
    )
    db.session.add(new_individual)
    db.session.commit()
    individual_out = IndividualOut.from_orm(new_individual)
    return jsonify(individual_out.model_dump()), 201


# Get All Individuals
@core_bp.route('/', methods=['GET'])
def get_individuals():
    individuals = Individual.query.all()
    individual_out_list = [IndividualOut.from_orm(individual) for
                           individual in individuals]
    individual_dicts = [individual_out.model_dump() for
                        individual_out in individual_out_list]
    return jsonify(individual_dicts), 200


# Get Individual by ID
@core_bp.route('/<int:id>', methods=['GET'])
def get_individual(id: int):
    individual = Individual.query.get_or_404(id)
    individual_out = IndividualOut.from_orm(individual)
    return jsonify(individual_out.model_dump()), 200


# Update Individual
@core_bp.route('/<int:id>', methods=['PUT'])
@validate()
def update_individual(id: int, body: IndividualUpdate):
    individual = Individual.query.get_or_404(id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(individual, key, value)
    db.session.commit()
    individual_out = IndividualOut.from_orm(individual)
    return jsonify(individual_out.model_dump()), 200


# Delete Individual
@core_bp.route('/<int:id>', methods=['DELETE'])
def delete_individual(id: int):
    individual = Individual.query.get_or_404(id)
    db.session.delete(individual)
    db.session.commit()
    return jsonify(
        {'message': 'Individual deleted successfully'}), 200
