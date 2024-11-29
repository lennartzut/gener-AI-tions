from .enums import RelationshipTypeEnum
from datetime import date
from app.extensions import db


class Family(db.Model):
    """
    Family model representing a family unit consisting of two partners and their union details.

    Attributes:
        id (int): Primary key.
        partner1_id (int): Foreign key referencing the first partner.
        partner2_id (int): Foreign key referencing the second partner.
        relationship_type (RelationshipTypeEnum): Type of relationship between the partners.
        union_date (date): Date when the union was established.
        union_place (str): Place where the union was established.
        dissolution_date (date): Date when the union was dissolved, if applicable.

    Relationships:
        partner1 (Individual): The first partner in the family.
        partner2 (Individual): The second partner in the family.
    """
    __tablename__ = 'families'
    __table_args__ = (
        db.UniqueConstraint('partner1_id', 'partner2_id',
                            name='uix_partners'),
        db.CheckConstraint('partner1_id < partner2_id',
                           name='chk_partner_order'),
        db.CheckConstraint(
            'dissolution_date IS NULL OR dissolution_date > union_date',
            name='chk_dissolution_after_union'),
    )

    id = db.Column(db.Integer, primary_key=True)
    partner1_id = db.Column(
        db.Integer,
        db.ForeignKey('individuals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    partner2_id = db.Column(
        db.Integer,
        db.ForeignKey('individuals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    relationship_type = db.Column(
        db.Enum(RelationshipTypeEnum),
        nullable=True
    )
    union_date = db.Column(db.Date, nullable=True)
    union_place = db.Column(db.String(100), nullable=True)
    dissolution_date = db.Column(db.Date, nullable=True)

    # Relationships
    partner1 = db.relationship(
        'Individual',
        foreign_keys=[partner1_id],
        back_populates='families_as_partner1'
    )
    partner2 = db.relationship(
        'Individual',
        foreign_keys=[partner2_id],
        back_populates='families_as_partner2'
    )

    def __repr__(self):
        """
        Returns a string representation of the Family instance.
        """
        return (
            f"<Family(id={self.id}, partner1_id={self.partner1_id}, "
            f"partner2_id={self.partner2_id}, relationship_type='{self.relationship_type.value if self.relationship_type else 'None'}')>"
        )

    # Helper Methods
    def is_active(self):
        """
        Determines if the family union is currently active.

        Returns:
            bool: True if active (no dissolution_date), False otherwise.
        """
        return self.dissolution_date is None

    def duration(self):
        """
        Calculates the duration of the family union.

        Returns:
            tuple: A tuple containing the start date and end date (if dissolved).
        """
        return (self.union_date, self.dissolution_date)

    def get_partners(self):
        """
        Retrieves both partners in the family.

        Returns:
            list: A list containing both partner1 and partner2 Individual instances.
        """
        return [self.partner1, self.partner2]
