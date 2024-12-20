# File: app/api/relationships.py

from flask import Blueprint, jsonify, request, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.relationship_schema import RelationshipCreate, RelationshipOut
from app.models.individual import Individual
from app.models.project import Project
from app.models.relationship import Relationship
from app.models.enums import FamilyRelationshipEnum
from app.extensions import db

api_relationships_bp = Blueprint('api_relationships_bp', __name__)

def get_project_or_404(user_id: int, project_id: int) -> Project:
    project = Project.query.filter_by(id=project_id,
                                      user_id=user_id).first()
    if not project:
        abort(404, description="Project not found or not owned by this user.")
    return project

@api_relationships_bp.route('/individual/<int:individual_id>', methods=['GET'])
@jwt_required()
def get_relationships(individual_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)

    try:
        individual = Individual.query.filter_by(
            id=individual_id,
            user_id=current_user_id,
            project_id=project_id
        ).first_or_404()

        # Fetch relationships with relationship_id
        # Parents: relationship_type='parent' where related_id=individual_id
        parent_relationships = Relationship.query.filter_by(
            relationship_type='parent',
            related_id=individual.id,
            project_id=project_id
        ).all()

        # Children: relationship_type='parent' where individual_id=individual_id
        child_relationships = Relationship.query.filter_by(
            relationship_type='parent',
            individual_id=individual.id,
            project_id=project_id
        ).all()

        # Partners: relationship_type='partner' where individual_id=individual.id or related_id=individual.id
        partner_relationships = Relationship.query.filter(
            Relationship.relationship_type == 'partner',
            Relationship.project_id == project_id
        ).filter(
            (Relationship.individual_id == individual.id) | (Relationship.related_id == individual.id)
        ).all()

        data = {
            'parents': [
                {
                    'relationship_id': rel.id,
                    'id': rel.individual.id,
                    'name': f"{rel.individual.primary_identity.first_name} {rel.individual.primary_identity.last_name}" if rel.individual.primary_identity else "Unknown Name"
                }
                for rel in parent_relationships
            ],
            'children': [
                {
                    'relationship_id': rel.id,
                    'id': rel.related.id,
                    'name': f"{rel.related.primary_identity.first_name} {rel.related.primary_identity.last_name}" if rel.related.primary_identity else "Unknown Name"
                }
                for rel in child_relationships
            ],
            'partners': [
                {
                    'relationship_id': rel.id,
                    'id': rel.related.id if rel.individual_id == individual.id else rel.individual.id,
                    'name': f"{rel.related.primary_identity.first_name} {rel.related.primary_identity.last_name}" if rel.related.primary_identity else "Unknown Name"
                }
                for rel in partner_relationships
            ],
        }

        return jsonify({'relationships': data}), 200

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error fetching relationships: {e}")
        return jsonify({'error': 'Database error occurred fetching relationships'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error fetching relationships: {e}")
        return jsonify({'error': 'Unexpected error occurred fetching relationships'}), 500

@api_relationships_bp.route('/', methods=['POST'])
@jwt_required()
def create_relationship():
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)

    try:
        data = request.get_json() or {}
        rel_data = RelationshipCreate(**data)

        # Validate individuals
        ind_main = Individual.query.filter_by(id=rel_data.individual_id,
                                              user_id=current_user_id,
                                              project_id=project_id).first()
        ind_other = Individual.query.filter_by(id=rel_data.related_id,
                                               user_id=current_user_id,
                                               project_id=project_id).first()

        if not ind_main or not ind_other:
            return jsonify({"error": "Individuals not found or not owned by the user."}), 404

        # Check if relationship exists
        existing = Relationship.query.filter_by(
            project_id=project_id,
            individual_id=rel_data.individual_id,
            related_id=rel_data.related_id,
            relationship_type=rel_data.relationship_type.value
        ).first()
        if existing:
            return jsonify({"message": "Relationship already exists", "relationship_id": existing.id}), 200

        # Create new relationship
        new_rel = Relationship(
            project_id=project_id,
            individual_id=rel_data.individual_id,
            related_id=rel_data.related_id,
            relationship_type=rel_data.relationship_type.value
        )
        db.session.add(new_rel)
        db.session.commit()

        # Automatic partner logic if we added a parent
        if rel_data.relationship_type == FamilyRelationshipEnum.PARENT:
            # This means individual_id=parent, related_id=child
            parent_id = rel_data.individual_id
            child_id = rel_data.related_id
            # Check if there's another parent for this child
            other_parent_rel = Relationship.query.filter(
                Relationship.project_id == project_id,
                Relationship.relationship_type == 'parent',
                Relationship.related_id == child_id,
                Relationship.individual_id != parent_id
            ).first()
            if other_parent_rel:
                other_parent_id = other_parent_rel.individual_id
                # Check if partner relationship exists
                partner_exist = Relationship.query.filter(
                    Relationship.project_id == project_id,
                    Relationship.relationship_type == 'partner'
                ).filter(
                    ((Relationship.individual_id == parent_id) & (Relationship.related_id == other_parent_id)) |
                    ((Relationship.individual_id == other_parent_id) & (Relationship.related_id == parent_id))
                ).first()
                if not partner_exist:
                    new_partner_rel = Relationship(
                        project_id=project_id,
                        individual_id=parent_id,
                        related_id=other_parent_id,
                        relationship_type='partner'
                    )
                    db.session.add(new_partner_rel)
                    db.session.commit()

        return jsonify({
            "message": "Relationship created successfully",
            "relationship_id": new_rel.id
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"DB error creating relationship: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating relationship: {e}")
        return jsonify({"error": "Unexpected error occurred"}), 500

@api_relationships_bp.route('/<int:relationship_id>', methods=['DELETE'])
@jwt_required()
def delete_relationship(relationship_id):
    current_user_id = get_jwt_identity()
    project_id = request.args.get('project_id', type=int)
    if not project_id:
        return jsonify({'error': 'project_id is required'}), 400

    get_project_or_404(current_user_id, project_id)

    try:
        # We only need to check that the 'individual' associated with this relationship
        # belongs to the current_user_id and project_id.
        # According to our model, 'individual_id' references the 'individuals' table.
        # We'll join to ensure user and project match.
        rel = (Relationship.query
               .join(Relationship.individual)
               .filter(Relationship.id == relationship_id,
                       Relationship.project_id == project_id,
                       Individual.user_id == current_user_id,
                       Individual.project_id == project_id)
               .first())

        if not rel:
            return jsonify({"error": "Relationship not found"}), 404

        db.session.delete(rel)
        db.session.commit()
        return jsonify({"message": "Relationship deleted successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"DB error deleting relationship {relationship_id}: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting relationship {relationship_id}: {e}")
        return jsonify({"error": "Unexpected error occurred"}), 500
