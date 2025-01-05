import logging
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.individual_model import Individual
from app.models.relationship_model import Relationship
from app.models.enums_model import InitialRelationshipEnum
from app.schemas.relationship_schema import RelationshipCreate, RelationshipUpdate
from app.utils.validators_utils import ValidationUtils

logger = logging.getLogger(__name__)


class RelationshipService:
    def __init__(self, db: Session):
        self.db = db

    def create_relationship(self, relationship_create: RelationshipCreate, project_id: int) -> Optional[Relationship]:
        """
        Creates a new relationship between two individuals within a project.
        """
        try:
            individual_id = relationship_create.individual_id
            related_id = relationship_create.related_id

            if individual_id == related_id:
                raise ValueError("An individual cannot have a relationship with themselves.")

            primary_individual = self.db.query(Individual).filter_by(id=individual_id, project_id=project_id).first()
            related_individual = self.db.query(Individual).filter_by(id=related_id, project_id=project_id).first()

            if not primary_individual or not related_individual:
                raise ValueError("Both individuals must belong to the same project.")

            ValidationUtils.validate_date_order(
                relationship_create.union_date,
                relationship_create.dissolution_date,
                "Union date must be before dissolution date."
            )

            new_relationship = Relationship(
                project_id=project_id,
                individual_id=individual_id,
                related_id=related_id,
                initial_relationship=relationship_create.initial_relationship,
                relationship_detail_horizontal=(
                    relationship_create.relationship_detail
                    if relationship_create.initial_relationship in {
                        InitialRelationshipEnum.CHILD,
                        InitialRelationshipEnum.PARENT}
                    else None
                ),
                relationship_detail_vertical=(
                    relationship_create.relationship_detail
                    if relationship_create.initial_relationship == InitialRelationshipEnum.PARTNER
                    else None
                ),
                union_date=relationship_create.union_date,
                union_place=relationship_create.union_place,
                dissolution_date=relationship_create.dissolution_date,
                notes=relationship_create.notes
            )

            self.db.add(new_relationship)
            self.db.commit()
            self.db.refresh(new_relationship)
            logger.info(f"Created new relationship: {new_relationship}")
            return new_relationship
        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error creating relationship: {e}")
            return None

    def update_relationship(self, relationship_id: int, relationship_update: RelationshipUpdate, project_id: int) -> Optional[Relationship]:
        """
        Updates an existing relationship's details.
        """
        try:
            relationship = self.get_relationship_by_id(relationship_id)
            if not relationship or relationship.project_id != project_id:
                raise ValueError("Relationship not found or unauthorized project access.")

            updates = relationship_update.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(relationship, field, value)

            ValidationUtils.validate_date_order(
                relationship.union_date,
                relationship.dissolution_date,
                "Union date must be before dissolution date."
            )

            self.db.commit()
            self.db.refresh(relationship)
            logger.info(f"Updated relationship: ID={relationship_id}")
            return relationship
        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error updating relationship: {e}")
            return None

    def delete_relationship(self, relationship_id: int, project_id: int) -> bool:
        """
        Deletes a relationship by ID.
        """
        try:
            relationship = self.get_relationship_by_id(relationship_id)
            if not relationship or relationship.project_id != project_id:
                raise ValueError("Relationship not found or unauthorized project access.")

            self.db.delete(relationship)
            self.db.commit()
            logger.info(f"Deleted relationship: ID={relationship_id}")
            return True
        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error deleting relationship: {e}")
            return False

    def get_relationship_by_id(self, relationship_id: int) -> Optional[Relationship]:
        """
        Fetches a specific relationship by ID.
        """
        try:
            return self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving relationship: {e}")
            return None

    def get_relationships_for_individual(self, project_id: int, individual_id: int) -> List[Relationship]:
        """
        Retrieves all relationships for a specific individual within a project.
        """
        try:
            relationships = self.db.query(Relationship).filter(
                Relationship.project_id == project_id,
                (Relationship.individual_id == individual_id) | (Relationship.related_id == individual_id)
            ).all()
            logger.debug(f"Fetched {len(relationships)} relationships for individual {individual_id}.")
            return relationships
        except SQLAlchemyError as e:
            logger.error(f"Error fetching relationships for individual {individual_id}: {e}")
            return []
