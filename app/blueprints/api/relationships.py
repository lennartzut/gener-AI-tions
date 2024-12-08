from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.schemas.relationship_request_schema import \
    RelationshipRequest
from app.models.individual import Individual
from app.models.relationship import Relationship
from app.models.family import Family
from app.models.enums import FamilyRelationshipEnum

# Define Blueprint
api_relationships_bp = Blueprint('api_relationships_bp', __name__)


@api_relationships_bp.route('/relationships', methods=['POST'])
@jwt_required()
def create_relationship():
    """
    Creates a new relationship between individuals.
    """
    try:
        # Validate incoming request body against RelationshipRequest schema
        body = RelationshipRequest(**request.get_json())

        # Get the current user identity
        current_user_id = get_jwt_identity()

        # Get the target and current individual
        target_individual = Individual.query.filter_by(
            id=body.target_id).first_or_404()
        current_individual = Individual.query.filter_by(
            id=current_user_id).first()

        if not current_individual:
            return jsonify({"error": "User not found"}), 404

        # Handle relationship creation
        if body.type == FamilyRelationshipEnum.PARENT:
            # Check if relationship already exists
            existing_relationship = Relationship.query.filter_by(
                parent_id=body.target_id,
                child_id=current_user_id,
                relationship_type=FamilyRelationshipEnum.PARENT
            ).first()

            if existing_relationship:
                return jsonify({
                                   "message": "Parent-child relationship already exists."}), 200

            # Create parent-child relationship
            new_relationship = Relationship(
                parent_id=body.target_id,
                child_id=current_user_id,
                relationship_type=FamilyRelationshipEnum.PARENT
            )
            db.session.add(new_relationship)

            # Check for existing family or create a new one
            family = Family.query.filter(
                Family.children.any(id=current_user_id)
            ).first()

            if not family:
                family = Family(partner1_id=body.target_id)
                db.session.add(family)

            family.children.append(current_individual)

        elif body.type == FamilyRelationshipEnum.CHILD:
            # Check if relationship already exists
            existing_relationship = Relationship.query.filter_by(
                parent_id=current_user_id,
                child_id=body.target_id,
                relationship_type=FamilyRelationshipEnum.CHILD
            ).first()

            if existing_relationship:
                return jsonify({
                                   "message": "Child-parent relationship already exists."}), 200

            # Create child-parent relationship
            new_relationship = Relationship(
                parent_id=current_user_id,
                child_id=body.target_id,
                relationship_type=FamilyRelationshipEnum.CHILD
            )
            db.session.add(new_relationship)

            # Check for existing family or create a new one
            family = Family.query.filter(
                Family.children.any(id=body.target_id)
            ).first()

            if not family:
                family = Family(partner1_id=current_user_id)
                db.session.add(family)

            family.children.append(target_individual)

        elif body.type == FamilyRelationshipEnum.PARTNER:
            # Create or update family relationship for partners
            family = Family.query.filter_by(
                partner1_id=current_user_id,
                partner2_id=None).first()

            if family:
                family.partner2_id = body.target_id
            else:
                family = Family(
                    partner1_id=current_user_id,
                    partner2_id=body.target_id,
                    relationship_type=FamilyRelationshipEnum.PARTNER
                )
                db.session.add(family)

        else:
            return jsonify(
                {"error": "Invalid relationship type"}), 400

        db.session.commit()
        return jsonify(
            {"message": "Relationship created successfully"}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error: {e}")
        return jsonify({"error": "A database error occurred"}), 500

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unexpected error: {e}")
        return jsonify({
                           "error": f"An unexpected error occurred: {str(e)}"}), 500
