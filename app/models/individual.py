from sqlalchemy.sql import func
from app.extensions import db


class Individual(db.Model):
    """
    Individual model representing a person with birth and death details.
    """
    __tablename__ = 'individuals'

    id = db.Column(db.Integer, primary_key=True)
    birth_date = db.Column(db.Date, nullable=True)
    birth_place = db.Column(db.String(100), nullable=True,
                            index=True)
    death_date = db.Column(db.Date, nullable=True)
    death_place = db.Column(db.String(100), nullable=True,
                            index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Relationships
    user = db.relationship(
        'User',
        back_populates='individuals'
    )
    identities = db.relationship(
        'Identity',
        back_populates='individual',
        cascade='all, delete-orphan'
    )
    families_as_partner1 = db.relationship(
        'Family',
        foreign_keys='Family.partner1_id',
        back_populates='partner1',
        cascade='all, delete-orphan'
    )
    families_as_partner2 = db.relationship(
        'Family',
        foreign_keys='Family.partner2_id',
        back_populates='partner2',
        cascade='all, delete-orphan'
    )
    parent_relationships = db.relationship(
        'Relationship',
        foreign_keys='Relationship.child_id',
        back_populates='child',
        cascade='all, delete-orphan'
    )
    child_relationships = db.relationship(
        'Relationship',
        foreign_keys='Relationship.parent_id',
        back_populates='parent',
        cascade='all, delete-orphan'
    )

    @property
    def primary_identity(self):
        """
        Returns the first identity associated with the individual, if any.
        """
        return self.identities[0] if self.identities else None

    def __repr__(self):
        """
        Returns a string representation of the Individual instance.
        """
        return f"<Individual(id={self.id}, birth_place='{self.birth_place}', birth_date={self.birth_date})>"

    # Helper Methods
    def get_parents(self):
        """
        Retrieves the parents of the individual.
        """
        return [rel.parent for rel in self.parent_relationships]

    def get_children(self):
        """
        Retrieves the children of the individual.
        """
        return [rel.child for rel in self.child_relationships]

    def get_siblings(self):
        """
        Retrieves the siblings of the individual.
        """
        return list({
            sibling
            for parent in self.get_parents()
            for sibling in parent.get_children()
            if sibling.id != self.id
        })

    def get_partners(self):
        """
        Retrieves the partners of the individual.
        """
        return list({
            family.partner2 for family in self.families_as_partner1
        }.union({
            family.partner1 for family in self.families_as_partner2
        }))
