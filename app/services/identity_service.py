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
        """
        self.db = db

    def create_identity(self, identity_create: IdentityCreate,
                        is_primary: bool = False) -> Optional[
        Identity]:
        """
        Creates a new identity for an individual.

        Automatically assigns an `identity_number` based on existing identities.
        If `is_primary` is True or the new identity's valid_from is later than
        the current primary's valid_from, the new identity is set as primary
        (with adjustment of the previous primary's valid_until).

        Raises:
            ValueError: If date constraints are violated.
            SQLAlchemyError: For any database-related errors.
        """
        try:
            max_identity_number = self.db.query(
                func.max(Identity.identity_number)
            ).filter(
                Identity.individual_id == identity_create.individual_id
            ).scalar()
            next_identity_number = 1 if max_identity_number is None else max_identity_number + 1

            # Create new identity (defaulting to non-primary)
            new_identity = Identity(**identity_create.model_dump(),
                                    is_primary=False)
            new_identity.identity_number = next_identity_number

            self.db.add(new_identity)
            self.db.flush()  # Flush to generate an ID for the new identity

            # Retrieve the current primary identity, if any
            current_primary = self.db.query(Identity).filter(
                Identity.individual_id == identity_create.individual_id,
                Identity.is_primary == True
            ).first()

            # If requested or if the new valid_from is later than the current primary's valid_from,
            # assign the new identity as primary.
            if is_primary or (
                    current_primary and
                    identity_create.valid_from and current_primary.valid_from and
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
        """
        try:
            identity = self.db.query(Identity).filter(
                Identity.id == identity_id
            ).first()
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
        If the identity is set to become primary, assigns it accordingly.
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
        If the deleted identity was primary, sets the next suitable identity as primary.
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
                    Identity.valid_from.desc().nullslast()).first()

                if new_primary:
                    new_primary.is_primary = True

                    next_identity = self.db.query(Identity).filter(
                        Identity.individual_id == individual_id,
                        Identity.valid_from > new_primary.valid_from
                    ).order_by(Identity.valid_from.asc()).first()

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
        Assigns a primary identity for an individual.
        Updates the previous primary's valid_until date and marks the new identity as primary.
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
                        if current_primary.valid_from and new_valid_until <= current_primary.valid_from:
                            raise ValueError(
                                "New valid_from date must be at least one day after the current primary's valid_from date.")
                        current_primary.valid_until = new_valid_until

                    current_primary.is_primary = False

            elif new_identity_id and current_primary and current_primary.id == new_identity_id:
                # Already primary, no changes needed.
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
