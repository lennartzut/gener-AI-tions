import logging
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.individual_model import Individual
from app.models.relationship_model import Relationship
from app.models.enums_model import InitialRelationshipEnum
from app.schemas.relationship_schema import RelationshipCreate, RelationshipUpdate
from app.utils.validators_utils import ValidationUtils

logger = logging.getLogger(__name__)


class RelationshipService:
    def __init__(self, db: Session):
        self.db = db

    def create_relationship(
        self,
        relationship_create: RelationshipCreate,
        project_id: int
    ) -> Optional[Relationship]:
        """
        Creates a new relationship between two individuals within a project.
        """

        try:
            individual_id = relationship_create.individual_id
            related_id = relationship_create.related_id

            if individual_id == related_id:
                logger.warning("Attempted to create a self-relationship.")
                return None

            # Ensure both individuals exist in the project
            primary_individual = self.db.query(Individual).filter_by(
                id=individual_id, project_id=project_id
            ).first()
            related_individual = self.db.query(Individual).filter_by(
                id=related_id, project_id=project_id
            ).first()

            if not primary_individual or not related_individual:
                logger.warning("Both individuals must belong to the same project.")
                return None

            # Check if this relationship already exists
            existing = self.db.query(Relationship).filter(
                Relationship.project_id == project_id,
                or_(
                    and_(
                        Relationship.individual_id == individual_id,
                        Relationship.related_id == related_id
                    ),
                    and_(
                        Relationship.individual_id == related_id,
                        Relationship.related_id == individual_id
                    )
                )
            ).first()
            if existing:
                raise ValueError("This relationship already exists.")

            # Validate date order (union_date <= dissolution_date)
            ValidationUtils.validate_date_order(
                relationship_create.union_date,
                relationship_create.dissolution_date,
                "Union date must be before dissolution date."
            )

            # Exclude 'relationship_detail' from direct constructor
            rel_data = relationship_create.model_dump(exclude={"relationship_detail"})

            # Create Relationship with the remaining fields
            new_rel = Relationship(
                project_id=project_id,
                **rel_data
            )

            # Manually set the correct column based on initial_relationship
            if relationship_create.initial_relationship == InitialRelationshipEnum.PARTNER:
                # For partners, store in vertical column
                new_rel.relationship_detail_vertical = relationship_create.relationship_detail
                new_rel.relationship_detail_horizontal = None
            else:
                # For child/parent, store in horizontal column
                new_rel.relationship_detail_horizontal = relationship_create.relationship_detail
                new_rel.relationship_detail_vertical = None

            self.db.add(new_rel)
            self.db.commit()
            self.db.refresh(new_rel)
            logger.info(f"Created relationship: ID={new_rel.id}")
            return new_rel

        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error creating relationship: {e}")
            return None

    def update_relationship(
        self,
        relationship_id: int,
        relationship_update: RelationshipUpdate,
        project_id: int
    ) -> Optional[Relationship]:
        """
        Updates an existing relationship's details.
        """

        try:
            relationship = self.get_relationship_by_id(relationship_id)
            if not relationship or relationship.project_id != project_id:
                raise ValueError("Relationship not found or unauthorized project access.")

            # Exclude 'relationship_detail' to avoid invalid constructor arg
            updates = relationship_update.model_dump(exclude={"relationship_detail"})

            for field, value in updates.items():
                setattr(relationship, field, value)

            # Check date order
            ValidationUtils.validate_date_order(
                relationship.union_date,
                relationship.dissolution_date,
                "Union date must be before dissolution date."
            )

            # If the updated payload includes a new relationship_detail,
            # set it in the correct column.
            if relationship_update.relationship_detail is not None:
                if relationship_update.initial_relationship == InitialRelationshipEnum.PARTNER:
                    relationship.relationship_detail_vertical = relationship_update.relationship_detail
                    relationship.relationship_detail_horizontal = None
                else:
                    relationship.relationship_detail_horizontal = relationship_update.relationship_detail
                    relationship.relationship_detail_vertical = None

            # Check for duplicates again (in case IDs changed)
            existing = self.db.query(Relationship).filter(
                Relationship.project_id == project_id
            ).filter(
                or_(
                    and_(
                        Relationship.individual_id == relationship.individual_id,
                        Relationship.related_id == relationship.related_id
                    ),
                    and_(
                        Relationship.individual_id == relationship.related_id,
                        Relationship.related_id == relationship.individual_id
                    )
                )
            ).first()

            if existing and existing.id != relationship_id:
                raise ValueError("This relationship already exists.")

            self.db.commit()
            self.db.refresh(relationship)
            logger.info(f"Updated relationship: ID={relationship_id}")
            return relationship

        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error updating relationship: {e}")
            return None

    def get_relationship_by_id(self, relationship_id: int) -> Optional[Relationship]:
        """
        Fetch a relationship by its ID.
        """
        try:
            rel = self.db.query(Relationship).filter(
                Relationship.id == relationship_id
            ).first()
            if not rel:
                logger.warning(f"Relationship not found: ID={relationship_id}")
            return rel
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving relationship: {e}")
            return None

    def list_relationships(self, project_id: int) -> List[Relationship]:
        """
        Retrieves all relationships in a given project.
        """
        try:
            rels = self.db.query(Relationship).filter(
                Relationship.project_id == project_id
            ).all()
            logger.info(f"Retrieved {len(rels)} relationships for project {project_id}")
            return rels
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error listing relationships: {e}")
            return []

    def delete_relationship(self, relationship_id: int, project_id: int) -> bool:
        """
        Deletes a relationship by ID.
        """
        try:
            rel = self.get_relationship_by_id(relationship_id)
            if not rel or rel.project_id != project_id:
                raise ValueError("Relationship not found or unauthorized project access.")

            self.db.delete(rel)
            self.db.commit()
            logger.info(f"Deleted relationship: ID={relationship_id}")
            return True
        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error deleting relationship: {e}")
            return False