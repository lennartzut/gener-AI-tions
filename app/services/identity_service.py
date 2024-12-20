from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.models.identity import Identity


class IdentityService:
    def __init__(self, db: Session):
        self.db = db

    def create_identity(self, individual_id: int, first_name: str,
                        last_name: str,
                        gender: str,
                        valid_from: Optional[date] = None,
                        valid_until: Optional[
                            date] = None) -> Identity:
        """Create a new identity."""
        new_identity = Identity(
            individual_id=individual_id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            valid_from=valid_from,
            valid_until=valid_until
        )
        self.db.add(new_identity)
        self.db.commit()
        self.db.refresh(new_identity)
        return new_identity

    def get_identity_by_id(self, identity_id: int) -> Optional[
        Identity]:
        """Fetch an identity by its ID."""
        return self.db.query(Identity).filter(
            Identity.id == identity_id).first()

    def update_identity(self, identity_id: int, **kwargs) -> \
    Optional[Identity]:
        """Update an identity's details."""
        identity = self.get_identity_by_id(identity_id)
        if not identity:
            return None

        for key, value in kwargs.items():
            if hasattr(identity, key):
                setattr(identity, key, value)

        self.db.commit()
        self.db.refresh(identity)
        return identity

    def delete_identity(self, identity_id: int) -> Optional[
        Identity]:
        """Delete an identity by its ID."""
        identity = self.get_identity_by_id(identity_id)
        if not identity:
            return None

        self.db.delete(identity)
        self.db.commit()
        return identity

    def list_identities_by_individual(self, individual_id: int) -> \
    List[Identity]:
        """List all identities for a given individual."""
        return self.db.query(Identity).filter(
            Identity.individual_id == individual_id).all()
