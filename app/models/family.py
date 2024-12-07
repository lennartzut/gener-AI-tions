"""
Defines the Family model, representing family units and their relationships.
"""

from app.extensions import db
from .enums import LegalRelationshipEnum
from .associations import family_children_association_table


class Family(db.Model):
    """
    Represents a family unit consisting of two partners and their children.
    """

    __tablename__ = 'families'

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
        nullable=True,  # Partner2 can be NULL (single-parent family)
        index=True
    )
    relationship_type = db.Column(
        db.Enum(LegalRelationshipEnum),
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
    children = db.relationship(
        'Individual',
        secondary=family_children_association_table,
        back_populates='families'
    )

    def __repr__(self):
        """
        Returns a string representation of the family instance.
        """
        partner2_repr = self.partner2_id if self.partner2_id else "None"
        return (
            f"<Family(id={self.id}, partner1_id={self.partner1_id}, "
            f"partner2_id={partner2_repr}, "
            f"relationship_type='{self.relationship_type.value if self.relationship_type else 'None'}')>"
        )

    # Helper Methods
    def is_active(self) -> bool:
        """
        Determines if the family union is currently active.
        :return: True if the union is active, otherwise False.
        """
        return self.dissolution_date is None

    def duration(self):
        """
        Calculates the duration of the family union.
        :return: A tuple containing the start (union_date) and end (dissolution_date) of the union.
        """
        return self.union_date, self.dissolution_date

    def get_partners(self):
        """
        Retrieves both partners in the family.
        :return: A list containing partner1 and partner2.
        """
        return [self.partner1, self.partner2] if self.partner2 else [
            self.partner1]
