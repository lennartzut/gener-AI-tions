"""
Defines the association table for family-children relationships.
"""

from app.extensions import db

# Association table for many-to-many relationships between families and children
family_children_association_table = db.Table(
    'family_children',
    db.Column(
        'family_id',
        db.Integer,
        db.ForeignKey('families.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    ),
    db.Column(
        'child_id',
        db.Integer,
        db.ForeignKey('individuals.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
)
