import logging
from typing import Optional, List

from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.enums_model import InitialRelationshipEnum
from app.models.individual_model import Individual
from app.models.relationship_model import Relationship
from app.schemas.relationship_schema import RelationshipCreate, \
    RelationshipUpdate
from app.utils.validators import ValidationUtils

logger = logging.getLogger(__name__)


class RelationshipService:
    """
    Service layer for managing relationships between individuals.
    Provides methods to create, retrieve, update, and delete relationships
    within a project, ensuring data integrity and adherence to business rules.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_relationship(self,
                            relationship_create: RelationshipCreate,
                            project_id: int) -> Optional[
        Relationship]:
        """
        Creates a new relationship between two individuals within a project,
        ensuring a single canonical row.
        """
        try:
            individual_id = relationship_create.individual_id
            related_id = relationship_create.related_id
            rel_type = relationship_create.initial_relationship
            detail = relationship_create.relationship_detail

            if individual_id == related_id:
                raise ValueError(
                    "Cannot create a self-relationship.")

            primary_individual = self.db.query(Individual).filter_by(
                id=individual_id, project_id=project_id
            ).first()
            related_individual = self.db.query(Individual).filter_by(
                id=related_id, project_id=project_id
            ).first()
            if not primary_individual or not related_individual:
                raise ValueError(
                    "Both individuals must belong to the same project.")

            existing_any_rel = self.db.query(Relationship).filter(
                Relationship.project_id == project_id
            ).filter(
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
            if existing_any_rel:
                raise ValueError(
                    "These two individuals already have a relationship. Multiple relationship types are not allowed.")

            if rel_type == InitialRelationshipEnum.CHILD:
                # For child, store as a parent relationship with reversed IDs.
                parent_id = related_id
                child_id = individual_id
                rel_type = InitialRelationshipEnum.PARENT
                individual_id = parent_id
                related_id = child_id

            if rel_type == InitialRelationshipEnum.PARTNER:
                # Ensure canonical order by sorting IDs.
                if related_id < individual_id:
                    individual_id, related_id = related_id, individual_id

            existing = self.db.query(Relationship).filter(
                Relationship.project_id == project_id
            ).filter(
                or_(
                    and_(
                        Relationship.individual_id == individual_id,
                        Relationship.related_id == related_id,
                        Relationship.initial_relationship == rel_type
                    ),
                    and_(
                        Relationship.individual_id == related_id,
                        Relationship.related_id == individual_id,
                        Relationship.initial_relationship == rel_type
                    )
                )
            ).first()

            if existing:
                raise ValueError("This relationship already exists.")

            # Validate the dates using the utility function.
            ValidationUtils.validate_date_order([
                (relationship_create.union_date,
                 relationship_create.dissolution_date,
                 "Union date must be before dissolution date.")
            ])

            new_rel = Relationship(
                project_id=project_id,
                individual_id=individual_id,
                related_id=related_id,
                initial_relationship=rel_type,
                union_date=relationship_create.union_date,
                union_place=relationship_create.union_place,
                dissolution_date=relationship_create.dissolution_date,
                notes=relationship_create.notes,
            )

            # Set relationship detail on the appropriate column.
            if rel_type == InitialRelationshipEnum.PARTNER:
                new_rel.relationship_detail_horizontal = detail
                new_rel.relationship_detail_vertical = None
            else:
                new_rel.relationship_detail_vertical = detail
                new_rel.relationship_detail_horizontal = None

            self.db.add(new_rel)
            self.db.commit()
            self.db.refresh(new_rel)
            logger.info(
                f"Created canonical relationship: ID={new_rel.id}")
            return new_rel

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error creating relationship: {e}")
            if "chk_relationship_dates" in str(e).lower():
                raise ValueError(
                    "Union date must be before dissolution date.")
            return None
        except ValueError as ve:
            self.db.rollback()
            logger.error(f"ValueError in create_relationship: {ve}")
            raise ve

    def update_relationship(self, relationship_id: int,
                            relationship_update: RelationshipUpdate,
                            project_id: int) -> Optional[
        Relationship]:
        """
        Updates an existing relationship's details, optionally re-canonicalizing
        if initial_relationship changes.
        """
        try:
            relationship = self.get_relationship_by_id(
                relationship_id)
            if not relationship or relationship.project_id != project_id:
                raise ValueError(
                    "Relationship not found or unauthorized project access.")

            original_ids = (
            relationship.individual_id, relationship.related_id)
            original_type = relationship.initial_relationship

            updates = relationship_update.model_dump(
                exclude_unset=True, exclude={"relationship_detail"})
            for field, value in updates.items():
                setattr(relationship, field, value)

            # Re-canonicalize if initial_relationship is updated.
            if relationship_update.initial_relationship:
                if relationship.initial_relationship == InitialRelationshipEnum.CHILD:
                    parent_id = relationship.related_id
                    child_id = relationship.individual_id
                    relationship.initial_relationship = InitialRelationshipEnum.PARENT
                    relationship.individual_id = parent_id
                    relationship.related_id = child_id
                elif relationship.initial_relationship == InitialRelationshipEnum.PARTNER:
                    if relationship.related_id < relationship.individual_id:
                        relationship.individual_id, relationship.related_id = (
                            relationship.related_id,
                            relationship.individual_id
                        )
                # For PARENT, no change is needed.

            if relationship_update.relationship_detail is not None:
                if relationship.initial_relationship == InitialRelationshipEnum.PARTNER:
                    relationship.relationship_detail_horizontal = relationship_update.relationship_detail
                    relationship.relationship_detail_vertical = None
                else:
                    relationship.relationship_detail_vertical = relationship_update.relationship_detail
                    relationship.relationship_detail_horizontal = None

            ValidationUtils.validate_date_order([
                (relationship.union_date,
                 relationship.dissolution_date,
                 "Union date must be before dissolution date.")
            ])

            existing = self.db.query(Relationship).filter(
                Relationship.project_id == project_id
            ).filter(
                or_(
                    and_(
                        Relationship.individual_id == relationship.individual_id,
                        Relationship.related_id == relationship.related_id,
                        Relationship.initial_relationship == relationship.initial_relationship
                    ),
                    and_(
                        Relationship.individual_id == relationship.related_id,
                        Relationship.related_id == relationship.individual_id,
                        Relationship.initial_relationship == relationship.initial_relationship
                    )
                )
            ).first()

            if existing and existing.id != relationship_id:
                raise ValueError(
                    "This relationship already exists with the new parameters.")

            self.db.commit()
            self.db.refresh(relationship)
            logger.info(
                f"Updated relationship: ID={relationship_id}")
            return relationship

        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error updating relationship: {e}")
            return None

    def get_relationship_by_id(self, relationship_id: int) -> \
    Optional[Relationship]:
        """
        Retrieves a relationship by its unique ID.
        """
        try:
            rel = self.db.query(Relationship).filter(
                Relationship.id == relationship_id).first()
            if not rel:
                logger.warning(
                    f"Relationship not found: ID={relationship_id}")
            return rel
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving relationship: {e}")
            return None

    def list_relationships(self, project_id: int) -> List[
        Relationship]:
        """
        Retrieves all relationships for a given project.
        """
        try:
            rels = self.db.query(Relationship).filter(
                Relationship.project_id == project_id).all()
            logger.info(
                f"Retrieved {len(rels)} relationships for project {project_id}")
            return rels
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error listing relationships: {e}")
            return []

    def delete_relationship(self, relationship_id: int,
                            project_id: int) -> bool:
        """
        Deletes a relationship by its ID.
        """
        try:
            rel = self.get_relationship_by_id(relationship_id)
            if not rel or rel.project_id != project_id:
                raise ValueError(
                    "Relationship not found or unauthorized project access.")

            self.db.delete(rel)
            self.db.commit()
            logger.info(
                f"Deleted relationship: ID={relationship_id}")
            return True
        except (ValueError, SQLAlchemyError) as e:
            self.db.rollback()
            logger.error(f"Error deleting relationship: {e}")
            return False
