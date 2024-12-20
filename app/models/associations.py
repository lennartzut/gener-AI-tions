from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

family_children_association_table = Table(
    'family_children',
    Base.metadata,
    Column(
        'family_id',
        Integer,
        ForeignKey('families.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    ),
    Column(
        'child_id',
        Integer,
        ForeignKey('individuals.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
)
