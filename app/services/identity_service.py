import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.identity_model import Identity
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
        If `is_primary` is True, unsets any existing primary identity.
        """
        try:
            if is_primary:
                self.unset_primary_identity(
                    identity_create.individual_id)

            ValidationUtils.validate_date_order(
                identity_create.valid_from,
                identity_create.valid_until,
                "Valid from date cannot be after valid until date."
            )

            new_identity = Identity(**identity_create.model_dump(),
                                    is_primary=is_primary)
            self.db.add(new_identity)
            self.db.commit()
            self.db.refresh(new_identity)
            logger.info(f"Created new identity: {new_identity}")
            return new_identity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error while creating identity: {e}")
            return None

    def get_identity_by_id(self, identity_id: int) -> Optional[
        Identity]:
        """
        Fetches an identity by its ID.
        """
        try:
            identity = self.db.query(Identity).filter(
                Identity.id == identity_id).first()
            if identity:
                logger.debug(f"Retrieved identity: ID={identity_id}")
            else:
                logger.warning(
                    f"Identity not found: ID={identity_id}")
            return identity
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while retrieving identity: {e}")
            return None

    def update_identity(self, identity_id: int,
                        identity_update: IdentityUpdate) -> Optional[
        Identity]:
        """
        Updates an identity's details using a Pydantic IdentityUpdate model.
        """
        try:
            identity = self.get_identity_by_id(identity_id)
            if not identity:
                logger.warning(
                    f"Identity not found: ID={identity_id}")
                return None

            updates = identity_update.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(identity, field, value)

            if updates.get("is_primary"):
                self.unset_primary_identity(identity.individual_id)

            ValidationUtils.validate_date_order(
                identity.valid_from,
                identity.valid_until,
                "Valid from date cannot be after valid until date."
            )

            self.db.commit()
            self.db.refresh(identity)
            logger.info(f"Updated identity: ID={identity_id}")
            return identity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error while updating identity: {e}")
            return None

    def delete_identity(self, identity_id: int) -> bool:
        """
        Deletes an identity by its ID.
        """
        try:
            identity = self.get_identity_by_id(identity_id)
            if not identity:
                logger.warning(
                    f"Identity not found for deletion: ID={identity_id}")
                return False

            self.db.delete(identity)
            self.db.commit()
            logger.info(f"Deleted identity: ID={identity_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Database error while deleting identity: {e}")
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
            logger.error(
                f"Database error while unsetting primary identity: {e}")
