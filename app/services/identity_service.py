import logging
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from app.models.identity_model import Identity
from app.models.individual_model import Individual
from app.schemas.identity_schema import IdentityCreate, \
    IdentityUpdate

logger = logging.getLogger(__name__)


class IdentityService:
    """
    Service layer for managing identities associated with individuals.

    Provides methods to create, retrieve, update, and delete identities,
    as well as manage primary identity assignments and validity periods.
    """

    def __init__(self, db: Session):
        """
        Initializes the IdentityService with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    def create_identity(self, identity_create: IdentityCreate,
                        is_primary: bool = False) -> Optional[
        Identity]:
        """
        Creates a new identity for an individual.

        Automatically assigns an `identity_number` based on
        existing identities.
        If `is_primary` is True or the `valid_from` date is later
        than the current primary's,
        the new identity is set as primary, and the previous
        primary's `valid_until` is updated.

        Args:
            identity_create (IdentityCreate): The schema
            containing identity details.
            is_primary (bool, optional): Flag indicating if the
            new identity should be primary. Defaults to False.

        Returns:
            Optional[Identity]: The newly created Identity object
            if successful, else None.

        Raises:
            ValueError: If the `valid_from` date is after the
            `valid_until` date.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            max_identity_number = self.db.query(
                func.max(Identity.identity_number)) \
                .filter(
                Identity.individual_id == identity_create.individual_id) \
                .scalar()
            next_identity_number = 1 if max_identity_number is None else max_identity_number + 1

            new_identity = Identity(**identity_create.model_dump(),
                                    is_primary=False)
            new_identity.identity_number = next_identity_number

            self.db.add(new_identity)
            self.db.flush()

            current_primary = self.db.query(Identity).filter(
                Identity.individual_id == identity_create.individual_id,
                Identity.is_primary == True
            ).first()

            if is_primary or (
                    current_primary and
                    identity_create.valid_from and
                    current_primary.valid_from and
                    identity_create.valid_from > current_primary.valid_from
            ):
                self.assign_primary_identity(
                    identity_create.individual_id,
                    new_identity.id,
                    identity_create.valid_from
                )

            self.db.commit()
            self.db.refresh(new_identity)
            logger.info(f"Created identity: ID={new_identity.id}")
            return new_identity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating identity: {e}")
            if "chk_validity_dates" in str(e).lower():
                raise ValueError(
                    "Valid from date cannot be after valid until date.")
            raise
        except ValueError as ve:
            self.db.rollback()
            logger.error(f"Validation error creating identity: {ve}")
            raise ve

    def get_identity_by_id(self, identity_id: int) -> Optional[
        Identity]:
        """
        Retrieves an identity by its unique identifier.

        Args:
            identity_id (int): The unique ID of the identity to retrieve.

        Returns:
            Optional[Identity]: The Identity object if found, else None.
        """
        try:
            identity = self.db.query(Identity).filter(
                Identity.id == identity_id).first()
            if not identity:
                logger.warning(
                    f"Identity not found: ID={identity_id}")
            return identity
        except SQLAlchemyError as e:
            logger.error(
                f"Error retrieving identity by ID {identity_id}: {e}")
            return None

    def get_all_identities(self, project_id: int) -> List[Identity]:
        """
        Retrieves all identities associated with a specific project.

        Args:
            project_id (int): The ID of the project whose
            identities are to be retrieved.

        Returns:
            List[Identity]: A list of Identity objects associated
            with the project.
        """
        try:
            identities = self.db.query(Identity).join(
                Individual).filter(
                Individual.project_id == project_id
            ).options(joinedload(Identity.individual)).all()
            logger.info(
                f"Retrieved {len(identities)} identities for project {project_id}")
            return identities
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Error retrieving identities for project {project_id}: {e}")
            return []

    def update_identity(self, identity_id: int,
                        identity_update: IdentityUpdate) -> Optional[
        Identity]:
        """
        Updates the details of an existing identity.

        If `is_primary` is set to True and the identity is not
        already primary, it assigns this identity as primary and
        updates the `valid_until` date of the previous primary
        identity accordingly.

        Args:
            identity_id (int): The unique ID of the identity to update.
            identity_update (IdentityUpdate): The schema
            containing updated identity details.

        Returns:
            Optional[Identity]: The updated Identity object if
            successful, else None.

        Raises:
            ValueError: If `valid_until` is not after `valid_from`.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            identity = self.get_identity_by_id(identity_id)
            if not identity:
                logger.warning(
                    f"Identity not found for update: ID={identity_id}")
                return None

            updates = identity_update.model_dump(exclude_unset=True)
            is_being_set_primary = updates.get("is_primary",
                                               identity.is_primary)

            if identity.is_primary and is_being_set_primary:
                for field, value in updates.items():
                    setattr(identity, field, value)
                self.db.commit()
                self.db.refresh(identity)
                logger.info(f"Updated identity: ID={identity_id}")
                return identity

            if is_being_set_primary:
                new_valid_from = updates.get("valid_from",
                                             identity.valid_from)
                self.assign_primary_identity(
                    individual_id=identity.individual_id,
                    new_identity_id=identity_id,
                    new_valid_from=new_valid_from
                )

            for field, value in updates.items():
                setattr(identity, field, value)

            self.db.commit()
            self.db.refresh(identity)
            logger.info(f"Updated identity: ID={identity_id}")
            return identity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating identity: {e}")
            return None
        except ValueError as ve:
            self.db.rollback()
            logger.error(f"Validation error updating identity: {ve}")
            raise ve

    def delete_identity(self, identity_id: int) -> bool:
        """
        Deletes an identity by its unique identifier.

        If the deleted identity was primary, the most recent
        remaining identity is set as the new primary. The
        `valid_until` date of the new primary
        is adjusted accordingly to maintain validity constraints.

        Args:
            identity_id (int): The unique ID of the identity to delete.

        Returns:
            bool: True if deletion was successful, else False.
        """
        try:
            identity = self.get_identity_by_id(identity_id)
            if not identity:
                logger.warning(
                    f"Identity not found for deletion: ID={identity_id}")
                return False

            individual_id = identity.individual_id
            was_primary = identity.is_primary

            self.db.delete(identity)
            self.db.commit()
            logger.info(f"Deleted identity: ID={identity_id}")

            if was_primary:
                new_primary = self.db.query(Identity).filter(
                    Identity.individual_id == individual_id
                ).order_by(
                    Identity.valid_from.desc().nullslast()
                ).first()

                if new_primary:
                    new_primary.is_primary = True

                    next_identity = self.db.query(Identity).filter(
                        Identity.individual_id == individual_id,
                        Identity.valid_from > new_primary.valid_from
                    ).order_by(
                        Identity.valid_from.asc()
                    ).first()

                    if next_identity:
                        new_primary.valid_until = next_identity.valid_from - timedelta(
                            days=1)

                    self.db.commit()
                    logger.info(
                        f"Set identity ID={new_primary.id} as primary for individual ID={individual_id}")

            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting identity: {e}")
            return False

    def assign_primary_identity(self, individual_id: int,
                                new_identity_id: Optional[
                                    int] = None,
                                new_valid_from: Optional[
                                    date] = None):
        """
        Assigns a primary identity for an individual, ensuring only one primary exists.

        If `new_identity_id` is provided and differs from the current primary,
        it sets the new identity as primary and updates the `valid_until` date
        of the previous primary identity to one day before the new `valid_from`.

        Args:
            individual_id (int): The ID of the individual whose primary identity is being set.
            new_identity_id (Optional[int], optional): The ID of the new primary identity. Defaults to None.
            new_valid_from (Optional[date], optional): The `valid_from` date for the new primary identity. Defaults to None.

        Raises:
            ValueError: If the new `valid_from` date is not at least one day after the current primary's `valid_from` date.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            current_primary = self.db.query(Identity).filter(
                Identity.individual_id == individual_id,
                Identity.is_primary == True
            ).first()

            if new_identity_id and current_primary and current_primary.id != new_identity_id:
                new_primary = self.db.query(Identity).filter(
                    Identity.id == new_identity_id
                ).first()
                if new_primary:
                    new_primary.is_primary = True

                    if new_valid_from:
                        new_valid_until = new_valid_from - timedelta(
                            days=1)
                        if new_valid_until <= current_primary.valid_from:
                            raise ValueError(
                                "New valid_from date must be at least one day after the current primary's valid_from date.")
                        current_primary.valid_until = new_valid_until

                    current_primary.is_primary = False

            elif new_identity_id and current_primary and current_primary.id == new_identity_id:
                pass

            elif not current_primary and new_identity_id:
                new_primary = self.db.query(Identity).filter(
                    Identity.id == new_identity_id
                ).first()
                if new_primary:
                    new_primary.is_primary = True

            self.db.commit()
            logger.info(
                f"Assigned primary identity for individual ID={individual_id}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error assigning primary identity: {e}")
            raise
        except ValueError as ve:
            self.db.rollback()
            logger.error(
                f"Validation error assigning primary identity: {ve}")
            raise ve
