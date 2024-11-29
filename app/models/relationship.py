from .enums import RelationshipType
from app.extensions import db


class Relationship(db.Model):
    """
    Relationship model representing the relationship between two individuals.

    Attributes:
        id (int): Primary key.
        parent_id (int): Foreign key referencing the parent individual.
        child_id (int): Foreign key referencing the child individual.
        relationship_type (RelationshipType): Type of relationship.

    Relationships:
        parent (Individual): The parent individual.
        child (Individual): The child individual.
    """
    __tablename__ = 'relationships'
    __table_args__ = (
        db.UniqueConstraint('parent_id', 'child_id',
                            'relationship_type',
                            name='uix_relationship'),
        db.CheckConstraint('parent_id != child_id',
                           name='chk_parent_child_not_same'),
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
        db.Enum(RelationshipType),
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
        Returns a string representation of the Relationship instance.
        """
        return (
            f"<Relationship(id={self.id}, parent_id={self.parent_id}, "
            f"child_id={self.child_id}, relationship_type='{self.relationship_type.value}')>"
        )
