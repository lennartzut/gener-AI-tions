from datetime import datetime, timezone
from extensions import db


class Individual(db.Model):
    __tablename__ = 'individuals'

    id = db.Column(db.Integer, primary_key=True)
    birth_date = db.Column(db.Date, nullable=True)
    birth_place = db.Column(db.String(100), nullable=True)
    death_date = db.Column(db.Date, nullable=True)
    death_place = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(
        timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(
        timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)

    # Relationships
    user = db.relationship(
        'User',
        back_populates='individuals'
    )
    identities = db.relationship(
        'Identity',
        back_populates='individual'
    )
    families_as_partner1 = db.relationship(
        'Family',
        foreign_keys='Family.partner1_id',
        back_populates='partner1'
    )
    families_as_partner2 = db.relationship(
        'Family',
        foreign_keys='Family.partner2_id',
        back_populates='partner2'
    )
    parent_relationships = db.relationship(
        'Relationship',
        foreign_keys='Relationship.child_id',
        back_populates='child',
        overlaps="child_relationships"
    )
    child_relationships = db.relationship(
        'Relationship',
        foreign_keys='Relationship.parent_id',
        back_populates='parent',
        overlaps="parent_relationships"
    )

    def __repr__(self):
        return f'<Individual id={self.id}, birth_place={self.birth_place}>'

    # Helper Methods
    def get_parents(self):
        return [rel.parent for rel in self.parent_relationships]

    def get_children(self):
        return [rel.child for rel in self.child_relationships]

    def get_siblings(self):
        siblings = set()
        for parent in self.get_parents():
            for sibling in parent.get_children():
                if sibling.id != self.id:
                    siblings.add(sibling)
        return list(siblings)

    def get_partners(self):
        partners = set()
        for family in self.families_as_partner1:
            partners.add(family.partner2)
        for family in self.families_as_partner2:
            partners.add(family.partner1)
        return list(partners)
