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
        """
        Initializes the RelationshipService with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    def create_relationship(self,
                            relationship_create: RelationshipCreate,
                            project_id: int) -> Optional[
        Relationship]:
        """
        Creates a new relationship between two individuals within a project.

        Args:
            relationship_create (RelationshipCreate): The schema containing relationship details.
            project_id (int): The ID of the project in which the relationship is being created.

        Returns:
            Optional[Relationship]: The newly created Relationship object if successful, else None.

        Raises:
            ValueError: If the relationship already exists or if date validations fail.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            individual_id = relationship_create.individual_id
            related_id = relationship_create.related_id

            if individual_id == related_id:
                logger.warning(
                    "Attempted to create a self-relationship.")
                return None

            primary_individual = self.db.query(Individual).filter_by(
                id=individual_id, project_id=project_id
            ).first()
            related_individual = self.db.query(Individual).filter_by(
                id=related_id, project_id=project_id
            ).first()

            if not primary_individual or not related_individual:
                logger.warning(
                    "Both individuals must belong to the same project.")
                return None

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

            ValidationUtils.validate_date_order([
                (relationship_create.union_date,
                 relationship_create.dissolution_date,
                 "Union date must be before dissolution date.")
            ])

            rel_data = relationship_create.model_dump(
                exclude={"relationship_detail"})

            new_rel = Relationship(
                project_id=project_id,
                **rel_data
            )

            if relationship_create.initial_relationship == InitialRelationshipEnum.PARTNER:
                new_rel.relationship_detail_vertical = relationship_create.relationship_detail
                new_rel.relationship_detail_horizontal = None
            else:
                new_rel.relationship_detail_horizontal = relationship_create.relationship_detail
                new_rel.relationship_detail_vertical = None

            self.db.add(new_rel)
            self.db.commit()
            self.db.refresh(new_rel)
            logger.info(f"Created relationship: ID={new_rel.id}")
            return new_rel

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error during Relationship creation: {e}")
            if "chk_relationship_dates" in str(e).lower():
                raise ValueError(
                    "Union date must be before dissolution date.")
            return None

    def update_relationship(self, relationship_id: int,
                            relationship_update: RelationshipUpdate,
                            project_id: int) -> Optional[
        Relationship]:
        """
        Updates an existing relationship's details.

        Args:
            relationship_id (int): The unique ID of the relationship to update.
            relationship_update (RelationshipUpdate): The schema containing updated relationship details.
            project_id (int): The ID of the project to which the relationship belongs.

        Returns:
            Optional[Relationship]: The updated Relationship object if successful, else None.

        Raises:
            ValueError: If the relationship does not exist or if validations fail.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            relationship = self.get_relationship_by_id(
                relationship_id)
            if not relationship or relationship.project_id != project_id:
                raise ValueError(
                    "Relationship not found or unauthorized project access.")

            updates = relationship_update.model_dump(
                exclude={"relationship_detail"})

            for field, value in updates.items():
                setattr(relationship, field, value)

            ValidationUtils.validate_date_order([
                (relationship.union_date,
                 relationship.dissolution_date,
                 "Union date must be before dissolution date.")
            ])

            if relationship_update.relationship_detail is not None:
                if relationship_update.initial_relationship == InitialRelationshipEnum.PARTNER:
                    relationship.relationship_detail_vertical = relationship_update.relationship_detail
                    relationship.relationship_detail_horizontal = None
                else:
                    relationship.relationship_detail_horizontal = relationship_update.relationship_detail
                    relationship.relationship_detail_vertical = None

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
        Fetches a relationship by its ID.

        Args:
            relationship_id (int): The unique ID of the relationship to retrieve.

        Returns:
            Optional[Relationship]: The Relationship object if found, else None.
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
        Retrieves all relationships in a given project.

        Args:
            project_id (int): The ID of the project whose relationships are to be retrieved.

        Returns:
            List[Relationship]: A list of Relationship objects associated with the project.
        """
        try:
            rels = self.db.query(Relationship).filter(
                Relationship.project_id == project_id
            ).all()
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
        Deletes a relationship by ID.

        Args:
            relationship_id (int): The unique ID of the relationship to delete.
            project_id (int): The ID of the project to which the relationship belongs.

        Returns:
            bool: True if deletion was successful, else False.

        Raises:
            ValueError: If the relationship does not exist or if access is unauthorized.
            SQLAlchemyError: For any database-related errors.
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
