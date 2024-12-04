"""
Individual model representing a person with birth, death details, and familial relationships.
"""

from sqlalchemy.sql import func
from app.extensions import db
from datetime import date
from .family import Family
from .associations import family_children_association_table


def get_family_by_parents(parent1_id, parent2_id):
    """
    Retrieves a family record based on two parent IDs.

    Args:
        parent1_id (int): ID of the first parent.
        parent2_id (int): ID of the second parent.

    Returns:
        Family: The family record if found, otherwise None.
    """
    return Family.query.filter(
        ((Family.partner1_id == parent1_id) & (
                Family.partner2_id == parent2_id)) |
        ((Family.partner1_id == parent2_id) & (
                Family.partner2_id == parent1_id))
    ).first()


class Individual(db.Model):
    """
    Represents an individual with birth, death, and familial relationships.
    """
    __tablename__ = 'individuals'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    birth_date = db.Column(db.Date, nullable=True)
    birth_place = db.Column(db.String(100), nullable=True,
                            index=True)
    death_date = db.Column(db.Date, nullable=True)
    death_place = db.Column(db.String(100), nullable=True,
                            index=True)
    created_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True
    )

    # Relationships
    user = db.relationship(
        'User', back_populates='individuals'
    )
    identities = db.relationship(
        'Identity', back_populates='individual',
        cascade='all, delete-orphan'
    )
    families_as_partner1 = db.relationship(
        'Family', foreign_keys='Family.partner1_id',
        back_populates='partner1', cascade='all, delete-orphan'
    )
    families_as_partner2 = db.relationship(
        'Family', foreign_keys='Family.partner2_id',
        back_populates='partner2', cascade='all, delete-orphan'
    )
    parent_relationships = db.relationship(
        'Relationship', foreign_keys='Relationship.child_id',
        back_populates='child', cascade='all, delete-orphan'
    )
    child_relationships = db.relationship(
        'Relationship', foreign_keys='Relationship.parent_id',
        back_populates='parent', cascade='all, delete-orphan'
    )
    families = db.relationship(
        'Family', secondary=family_children_association_table,
        back_populates='children'
    )

    # Properties
    @property
    def primary_identity(self):
        """
        Returns the primary identity of the individual.
        If no identity exists, returns None.
        """
        return self.identities[0] if self.identities else None

    # Helper Methods
    def get_parents(self):
        """
        Retrieves the parents of the individual.

        Returns:
            List[Individual]: A list of parent individuals.
        """
        return [rel.parent for rel in self.parent_relationships]

    def get_children(self, partner_id=None):
        """
        Retrieves the children of the individual.
        If a partner_id is provided, retrieves children with that specific partner.

        Args:
            partner_id (int, optional): ID of the partner to filter children by.

        Returns:
            List[Individual]: A list of child individuals.
        """
        if partner_id:
            families = Family.query.filter(
                ((Family.partner1_id == self.id) & (
                        Family.partner2_id == partner_id)) |
                ((Family.partner1_id == partner_id) & (
                        Family.partner2_id == self.id))
            ).all()
            children = {child for family in families for child in
                        family.children}
            return list(children)
        return [rel.child for rel in self.child_relationships]

    def get_siblings(self):
        """
        Retrieves the siblings of the individual, excluding the individual themselves.

        Returns:
            List[Individual]: A list of sibling individuals.
        """
        siblings = set()
        for parent in self.get_parents():
            for sibling in parent.get_children():
                if sibling.id != self.id:
                    siblings.add(sibling)
        return list(siblings)

    def get_partners(self):
        """
        Retrieves the partners of the individual.

        Returns:
            List[Individual]: A list of partner individuals.
        """
        partners = {family.partner2 for family in
                    self.families_as_partner1}
        partners.update({family.partner1 for family in
                         self.families_as_partner2})
        return list(partners)

    def get_age(self):
        """
        Calculates the age of the individual based on their birth and death dates.

        Returns:
            int: The individual's age in years, or None if the birth date is unavailable.
        """
        if not self.birth_date:
            return None
        end_date = self.death_date or date.today()
        return end_date.year - self.birth_date.year - (
                (end_date.month, end_date.day) < (
            self.birth_date.month, self.birth_date.day)
        )

    def __repr__(self):
        """
        Provides a string representation of the Individual instance.

        Returns:
            str: A string describing the individual.
        """
        return f"<Individual(id={self.id}, birth_place='{self.birth_place}', birth_date={self.birth_date})>"
