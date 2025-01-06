import logging
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.individual_model import Individual
from app.models.relationship_model import Relationship
from app.models.enums_model import InitialRelationshipEnum
from app.schemas.relationship_schema import RelationshipCreate, \
    RelationshipUpdate
from app.utils.validators_utils import ValidationUtils

logger = logging.getLogger(__name__)

class RelationshipService:
    def __init__(self, db: Session):
        self.db = db

    def create_relationship(self,
                            relationship_create: RelationshipCreate,
                            project_id: int) -> Optional[
        Relationship]:
        """
        Creates a new relationship between two individuals within a project, using a single canonical representation.
        """
        try:
            individual_id = relationship_create.individual_id
            related_id = relationship_create.related_id

            if individual_id == related_id:
                raise ValueError(
                    "An individual cannot have a relationship with themselves.")

            # Ensure both individuals exist in the same project
            primary_individual = self.db.query(Individual).filter_by(
                id=individual_id, project_id=project_id
            ).first()
            related_individual = self.db.query(Individual).filter_by(
                id=related_id, project_id=project_id
            ).first()

            if not primary_individual or not related_individual:
                raise ValueError(
                    "Both individuals must belong to the same project.")

            # Dump schema into a dictionary
            relationship_data = relationship_create.model_dump()

            # Map `relationship_detail` to the correct field
            if relationship_create.initial_relationship in {
                InitialRelationshipEnum.CHILD,
                InitialRelationshipEnum.PARENT
            }:
                relationship_data[
                    "relationship_detail_horizontal"] = relationship_data.pop(
                    "relationship_detail", None
                )
            elif relationship_create.initial_relationship == InitialRelationshipEnum.PARTNER:
                relationship_data[
                    "relationship_detail_vertical"] = relationship_data.pop(
                    "relationship_detail", None
                )

            # Remove any unused fields (e.g., `relationship_detail` if it was mapped)
            relationship_data.pop("relationship_detail", None)

            # Validate dates
            ValidationUtils.validate_date_order(
                relationship_create.union_date,
                relationship_create.dissolution_date,
                "Union date must be before dissolution date."
            )

            # Check if the relationship already exists (in either direction)
            existing_relationship = self.db.query(
                Relationship).filter(
                Relationship.project_id == project_id,
                ((Relationship.individual_id == individual_id) & (
                            Relationship.related_id == related_id)) |
                ((Relationship.individual_id == related_id) & (
                            Relationship.related_id == individual_id))
            ).first()

            if existing_relationship:
                raise ValueError("This relationship already exists.")

            # Create a single canonical relationship record
            new_relationship = Relationship(
                project_id=project_id,
                **relationship_data
            )
            self.db.add(new_relationship)
            self.db.commit()
            self.db.refresh(new_relationship)

            logger.info(
                f"Created new relationship: ID {new_relationship.id}")
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

            # Validate updated dates
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
            relationship = self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
            if not relationship:
                logger.warning(f"Relationship {relationship_id} not found.")
            return relationship
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving relationship: {e}")
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
            logger.info(f"Fetched {len(relationships)} relationships for individual {individual_id}.")
            return relationships
        except SQLAlchemyError as e:
            logger.error(f"Error fetching relationships for individual {individual_id}: {e}")
            return []
