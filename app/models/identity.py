"""
Identity model representing personal details associated with an individual.
"""

from datetime import date
from sqlalchemy import CheckConstraint, UniqueConstraint, Enum
from app.extensions import db
from app.models.enums import GenderEnum


class Identity(db.Model):
    """
    Represents an identity tied to an individual, with attributes like name, gender, and validity period.
    """
    __tablename__ = 'identities'

    __table_args__ = (
        # Ensure unique identity validity periods for each individual
        UniqueConstraint('individual_id', 'valid_from',
                         'valid_until',
                         name='uix_identity_validity'),
        # Ensure valid_from is earlier than valid_until
        CheckConstraint(
            'valid_until IS NULL OR valid_until > valid_from',
            name='chk_validity_dates'
        ),
    )

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    individual_id = db.Column(
        db.Integer,
        db.ForeignKey('individuals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    gender = db.Column(Enum(GenderEnum), nullable=True)
    valid_from = db.Column(db.Date, nullable=True)
    valid_until = db.Column(db.Date, nullable=True)

    # Relationships
    individual = db.relationship(
        'Individual', back_populates='identities'
    )

    # Representation
    def __repr__(self):
        """
        Provides a string representation of the Identity instance.

        Returns:
            str: A formatted string with identity details.
        """
        return (
            f"<Identity(id={self.id}, first_name='{self.first_name}', "
            f"last_name='{self.last_name}', gender='{self.gender.value if self.gender else 'None'}')>"
        )

    # Helper Methods
    def full_name(self):
        """
        Combines first and last names into a full name.

        Returns:
            str: Full name or "Unnamed" if both first and last names are missing.
        """
        names = [self.first_name, self.last_name]
        return ' '.join(filter(None, names)).strip() or "Unnamed"

    def is_valid(self):
        """
        Checks if the identity is valid based on current date and validity period.

        Returns:
            bool: True if the identity is valid, False otherwise.
        """
        today = date.today()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True
