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
    updated_at = db.Column(db.DateTime, default=datetime.now(
                               timezone.utc),
                           onupdate=datetime.now(
                               timezone.utc))

    # Relationships
    user = db.relationship(
        'User',
        back_populates='individuals'
    )
    identities = db.relationship(
        'Identity',
        back_populates='individual')
    families_as_partner1 = db.relationship(
        'Family',
        foreign_keys='Family.partner1_id',
        backref='partner1_family',
        overlaps="families_as_partner2, partner1"
    )
    families_as_partner2 = db.relationship(
        'Family',
        foreign_keys='Family.partner2_id',
        backref='partner2_family',
        overlaps="families_as_partner1, partner2"
    )
    children_relationships = db.relationship(
        'Relationship',
        foreign_keys='Relationship.parent_id',
        backref='parent_relationship',
        overlaps="parent_relationship, children_relationships"
    )
    parent_relationships = db.relationship(
        'Relationship',
        foreign_keys='Relationship.related_individual_id',
        backref='child_relationship',
        overlaps="child_relationship, parent_relationships"
    )

    def __repr__(self):
        return f'<Individual id={self.id}, birth_place={self.birth_place}>'

    # Helper Methods
    def get_parents(self):
        return [rel.parent_relationship for rel in self.parent_relationships]

    def get_children(self):
        return [rel.child_relationship for rel in self.children_relationships]

    def get_siblings(self):
        siblings = set()
        for parent in self.get_parents():
            for sibling in parent.get_children():
                if sibling.id != self.id:
                    siblings.add(sibling)
        return list(siblings)

    def get_partners(self):
        partners = []
        for family in self.families_as_partner1:
            if family.partner2_id != self.id:
                partners.append(family.partner2)
        for family in self.families_as_partner2:
            if family.partner1_id != self.id:
                partners.append(family.partner1)
        return partners
