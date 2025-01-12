import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.models.identity_model import Identity
from app.models.individual_model import Individual
from app.schemas.identity_schema import IdentityCreate, \
    IdentityUpdate
from app.utils.validators_utils import ValidationUtils

logger = logging.getLogger(__name__)


class IdentityService:
    def __init__(self, db: Session):
        self.db = db

    def create_identity(self, identity_create: IdentityCreate,
                        is_primary: bool = False) -> Optional[
        Identity]:
        """
        Creates a new identity for an individual.
        Automatically sets as primary if it's the latest identity based on `valid_from`.
        """
        try:
            ValidationUtils.validate_date_order(
                identity_create.valid_from,
                identity_create.valid_until,
                "Valid from date cannot be after valid until date."
            )

            new_identity = Identity(**identity_create.model_dump(),
                                    is_primary=is_primary)
            self.db.add(new_identity)
            self.db.flush()

            latest_identity = self.db.query(Identity).filter(
                Identity.individual_id == identity_create.individual_id
            ).order_by(
                Identity.valid_from.desc().nullslast()).first()

            if latest_identity and new_identity.id == latest_identity.id:
                self.unset_primary_identity(
                    identity_create.individual_id)
                new_identity.is_primary = True

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
            return None
        except ValueError as ve:
            self.db.rollback()
            logger.error(f"Validation error creating identity: {ve}")
            raise ve  # Let it propagate to be handled by route or global handler

    def get_identity_by_id(self, identity_id: int) -> Optional[
        Identity]:
        """
        Fetches an identity by its ID.
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
        Fetches all identities for a given project by associating with individuals.
        """
        try:
            identities = self.db.query(Identity).join(Individual).filter(
                Individual.project_id == project_id
            ).options(
                joinedload(Identity.individual)
            ).all()
            logger.info(f"Retrieved {len(identities)} identities for project {project_id}")
            return identities
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving identities for project {project_id}: {e}")
            return []

    def update_identity(self, identity_id: int,
                        identity_update: IdentityUpdate) -> Optional[
        Identity]:
        """
        Updates an identity's details.
        Automatically sets as primary if it's the latest identity based on `valid_from`.
        """
        try:
            identity = self.get_identity_by_id(identity_id)
            if not identity:
                logger.warning(
                    f"Identity not found for update: ID={identity_id}")
                return None

            updates = identity_update.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(identity, field, value)

            # Validate date order after updates
            ValidationUtils.validate_date_order(
                identity.valid_from,
                identity.valid_until,
                "Valid from date cannot be after valid until date."
            )

            # Check if this identity should be primary
            if updates.get("valid_from") or updates.get("valid_until"):
                latest_identity = self.db.query(Identity).filter(
                    Identity.individual_id == identity.individual_id
                ).order_by(
                    Identity.valid_from.desc().nullslast()
                ).first()

                if latest_identity and identity.id == latest_identity.id:
                    self.unset_primary_identity(identity.individual_id)
                    identity.is_primary = True

            # If explicitly setting as primary
            if updates.get("is_primary"):
                self.unset_primary_identity(identity.individual_id)
                identity.is_primary = True

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
            raise ve  # Let it propagate to be handled by route or global handler

    def delete_identity(self, identity_id: int) -> bool:
        """
        Deletes an identity by its ID.
        After deletion, sets the latest remaining identity as primary if any.
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
                # Set the latest remaining identity as primary
                latest_identity = self.db.query(Identity).filter(
                    Identity.individual_id == individual_id
                ).order_by(
                    Identity.valid_from.desc().nullslast()
                ).first()

                if latest_identity:
                    latest_identity.is_primary = True
                    self.db.commit()
                    logger.info(f"Set identity ID={latest_identity.id} as primary for individual ID={individual_id}")

            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting identity: {e}")
            return False

    def unset_primary_identity(self, individual_id: int):
        """
        Unsets any existing primary identity for an individual.
        """
        try:
            primary_identity = self.db.query(Identity).filter(
                Identity.individual_id == individual_id,
                Identity.is_primary.is_(True)
            ).first()
            if primary_identity:
                primary_identity.is_primary = False
                self.db.commit()
                logger.info(
                    f"Unset primary identity: ID={primary_identity.id}")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error unsetting primary identity: {e}")