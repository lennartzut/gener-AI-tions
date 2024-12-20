from flask import Blueprint, jsonify, request, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.models.individual import Individual
from app.models.project import Project
from app.models.identity import Identity
from app.schemas.individual_schema import (IndividualCreate,
                                           IndividualUpdate,
                                           IndividualOut)
from datetime import datetime
from typing import Optional
from app.extensions import db

api_individuals_bp = Blueprint('api_individuals', __name__)


def parse_date(date_str: Optional[str]):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_app.logger.error(
                f"Invalid date format: {date_str}")
            abort(400,
                  description="Invalid date format. Use 'YYYY-MM-DD'.")
    return None


def get_project_or_404(user_id: int, project_id: int) -> Project:
    project = Project.query.filter_by(id=project_id,
                                      user_id=user_id).first()
    if not project:
        abort(404,
              description="Project not found or not owned by this user.")
    return project


@api_individuals_bp.route('/', methods=['GET'])
@jwt_required()
def list_individuals():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_project_or_404(current_user_id, project_id)
    try:
        search_query = request.args.get('q', '').strip()
        query = Individual.query.filter_by(user_id=current_user_id,
                                           project_id=project_id)
        if search_query:
            query = query.join(Identity).filter(
                (Identity.first_name.ilike(f'%{search_query}%')) | (
                    Identity.last_name.ilike(f'%{search_query}%')))
        individuals = query.order_by(
            Individual.created_at.desc()).all()
        results = [IndividualOut.from_orm(ind).model_dump() for ind
                   in individuals]
        return jsonify({"data": results}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error listing individuals: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500


@api_individuals_bp.route('/<int:individual_id>', methods=['GET'])
@jwt_required()
def get_individual(individual_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_project_or_404(current_user_id, project_id)
    try:
        individual = Individual.query.filter_by(id=individual_id,
                                                user_id=current_user_id,
                                                project_id=project_id).first_or_404()
        return jsonify({"data": IndividualOut.from_orm(
            individual).model_dump()}), 200
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"Database error retrieving individual: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500


@api_individuals_bp.route('/', methods=['POST'])
@jwt_required()
def create_individual():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    try:
        data = request.get_json() or {}
        data['project_id'] = project_id
        data['user_id'] = current_user_id
        individual_create = IndividualCreate(**data)
        new_individual = Individual(
            user_id=current_user_id,
            project_id=project_id,
            birth_date=individual_create.birth_date,
            birth_place=individual_create.birth_place,
            death_date=individual_create.death_date,
            death_place=individual_create.death_place,
            notes=None
        )
        db.session.add(new_individual)
        db.session.flush()
        new_identity = Identity(
            individual_id=new_individual.id,
            first_name=individual_create.first_name,
            last_name=individual_create.last_name,
            gender=individual_create.gender,
            valid_from=individual_create.birth_date,
            is_primary=True
        )
        db.session.add(new_identity)
        db.session.commit()
        response_data = IndividualOut.from_orm(
            new_individual).model_dump()
        return jsonify({'message': 'Individual created successfully',
                        'data': response_data}), 201
    except AttributeError as e:
        current_app.logger.error(
            f"AttributeError during creation: {e}")
        return jsonify(
            {'error': 'Attribute error', 'details': str(e)}), 500
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error creating individual: {e}")
        return jsonify(
            {'error': 'Database error', 'details': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error creating individual: {e}")
        return jsonify({'error': 'Unexpected error occurred',
                        'details': str(e)}), 500


@api_individuals_bp.route('/search', methods=['GET'])
@jwt_required()
def search_individuals():
    try:
        current_user_id = get_jwt_identity()
        search_query = request.args.get('q', '').strip()
        exclude_ids = request.args.getlist('exclude_ids', type=int)
        project_id = request.args.get('project_id', type=int)

        if not project_id:
            return jsonify({'error': 'project_id is required'}), 400
        get_project_or_404(current_user_id, project_id)

        # Build query
        query = (Individual.query
                 .filter(Individual.user_id == current_user_id, Individual.project_id == project_id)
                 .join(Identity))

        if search_query:
            query = query.filter(
                (Identity.first_name.ilike(f'%{search_query}%')) |
                (Identity.last_name.ilike(f'%{search_query}%'))
            )

        if exclude_ids:
            query = query.filter(~Individual.id.in_(exclude_ids))

        # Sort and limit results
        query = query.order_by(Identity.first_name.asc()).limit(50)
        individuals = query.all()

        result = [
            {
                'id': ind.id,
                'name': f"{ind.primary_identity.first_name} {ind.primary_identity.last_name}"
                if ind.primary_identity else "Unknown Name"
            }
            for ind in individuals
        ]

        return jsonify({'individuals': result}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error during individual search: {e}")
        return jsonify({'error': 'Database error occurred during search'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error during search: {e}")
        return jsonify({'error': 'Unexpected error occurred during search'}), 500





@api_individuals_bp.route('/<int:individual_id>', methods=['PUT'])
@jwt_required()
def update_individual(individual_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_project_or_404(current_user_id, project_id)
    try:
        individual = Individual.query.filter_by(id=individual_id,
                                                user_id=current_user_id,
                                                project_id=project_id).first_or_404()
        data = request.get_json() or {}
        ind_update = IndividualUpdate(**data)
        for key, value in ind_update.dict(
                exclude_unset=True).items():
            setattr(individual, key, value)
        db.session.commit()
        return jsonify({"message": "Individual updated successfully",
                        "data": IndividualOut.from_orm(
                            individual).model_dump()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error updating individual: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error updating individual: {e}")
        return jsonify(
            {"error": "Invalid data", "details": str(e)}), 400


@api_individuals_bp.route('/<int:individual_id>', methods=['DELETE'])
@jwt_required()
def delete_individual(individual_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400
    get_project_or_404(current_user_id, project_id)
    try:
        individual = Individual.query.filter_by(id=individual_id,
                                                user_id=current_user_id,
                                                project_id=project_id).first_or_404()
        db.session.delete(individual)
        db.session.commit()
        return jsonify(
            {"message": "Individual deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(
            f"Database error deleting individual: {e}")
        return jsonify(
            {"error": "Database error", "details": str(e)}), 500
