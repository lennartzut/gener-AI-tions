from sqlalchemy.dialects.postgresql import ENUM
from app.schemas.enums import GenderEnum
from datetime import date
from app.extensions import db


class Identity(db.Model):
    """
    Identity model representing personal details associated with an individual.

    Attributes:
        id (int): Primary key.
        individual_id (int): Foreign key referencing the Individual.
        first_name (str): First name of the individual.
        last_name (str): Last name of the individual.
        gender (GenderEnum): Gender of the individual.
        valid_from (date): Start date of the identity's validity.
        valid_until (date): End date of the identity's validity.

    Relationships:
        individual (Individual): The individual associated with this identity.
    """
    __tablename__ = 'identities'
    __table_args__ = (
        db.UniqueConstraint('individual_id', 'valid_from',
                            'valid_until',
                            name='uix_identity_validity'),
        db.CheckConstraint(
            'valid_until IS NULL OR valid_until > valid_from',
            name='chk_validity_dates'),
    )

    id = db.Column(db.Integer, primary_key=True)
    individual_id = db.Column(
        db.Integer,
        db.ForeignKey('individuals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    gender = db.Column(
        ENUM(GenderEnum, name='genderenum', create_type=False),
        nullable=True)
    valid_from = db.Column(db.Date, nullable=True)
    valid_until = db.Column(db.Date, nullable=True)

    # Relationships
    individual = db.relationship(
        'Individual',
        back_populates='identities'
    )

    def __repr__(self):
        """
        Returns a string representation of the Identity instance.
        """
        return (
            f"<Identity(id={self.id}, first_name='{self.first_name}', "
            f"last_name='{self.last_name}', gender='{self.gender.value if self.gender else 'None'}')>"
        )

    # Helper Methods
    def full_name(self):
        """
        Returns the full name by combining first and last names.

        Returns:
            str: Full name of the individual.
        """
        names = [self.first_name, self.last_name]
        return ' '.join(filter(None, names)).strip() or "Unnamed"

    def is_valid(self):
        """
        Checks if the identity is currently valid based on the dates.

        Returns:
            bool: True if valid, False otherwise.
        """
        today = date.today()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True
