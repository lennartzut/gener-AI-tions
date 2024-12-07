"""
Defines the Relationship model, representing parent-child or guardian relationships.
"""

from sqlalchemy import CheckConstraint, UniqueConstraint
from app.extensions import db
from .enums import FamilyRelationshipEnum


class Relationship(db.Model):
    """
    Represents a relationship between two individuals, such as parent-child or guardian-child.
    """

    __tablename__ = 'relationships'
    __table_args__ = (
        UniqueConstraint(
            'parent_id', 'child_id', 'relationship_type',
            name='uix_relationship'
        ),
        CheckConstraint(
            'parent_id != child_id',
            name='chk_parent_child_not_same'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('individuals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    child_id = db.Column(
        db.Integer,
        db.ForeignKey('individuals.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    relationship_type = db.Column(
        db.Enum(FamilyRelationshipEnum),
        nullable=False
    )

    # Relationships
    parent = db.relationship(
        'Individual',
        foreign_keys=[parent_id],
        back_populates='child_relationships'
    )
    child = db.relationship(
        'Individual',
        foreign_keys=[child_id],
        back_populates='parent_relationships'
    )

    def __repr__(self):
        """
        Returns a string representation of the relationship instance.
        """
        return (
            f"<Relationship(id={self.id}, parent_id={self.parent_id}, "
            f"child_id={self.child_id}, relationship_type='{self.relationship_type.value}')>"
        )
