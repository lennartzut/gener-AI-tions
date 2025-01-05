from sqlalchemy import Column, Integer, String, Date, DateTime, \
    ForeignKey, CheckConstraint, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_model import Base
from app.models.enums_model import InitialRelationshipEnum, \
    HorizontalRelationshipTypeEnum, VerticalRelationshipTypeEnum


class Relationship(Base):
    __tablename__ = 'relationships'
    __table_args__ = (
        CheckConstraint('individual_id != related_id',
                        name='chk_relationship_no_self'),
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id',
                                            ondelete='CASCADE'),
                        nullable=False, index=True)
    individual_id = Column(Integer, ForeignKey('individuals.id',
                                               ondelete='CASCADE'),
                           nullable=False, index=True)
    related_id = Column(Integer, ForeignKey('individuals.id',
                                            ondelete='CASCADE'),
                        nullable=False, index=True)

    initial_relationship = Column(SAEnum(InitialRelationshipEnum,
                                         name='initial_relationship_enum'),
                                  nullable=False)
    relationship_detail_horizontal = Column(
        SAEnum(HorizontalRelationshipTypeEnum,
               name='horizontal_relationship_enum'), nullable=True)
    relationship_detail_vertical = Column(
        SAEnum(VerticalRelationshipTypeEnum,
               name='vertical_relationship_enum'), nullable=True)

    union_date = Column(Date, nullable=True)
    union_place = Column(String(100), nullable=True)
    dissolution_date = Column(Date, nullable=True)
    notes = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship('Project', back_populates='relationships')
    individual = relationship('Individual',
                              foreign_keys=[individual_id],
                              back_populates='relationships_as_individual',
                              lazy='joined')
    related = relationship('Individual', foreign_keys=[related_id],
                           back_populates='relationships_as_related',
                           lazy='joined')

    def validate_relationship(self):
        """Validates the relationship to ensure consistency."""
        if self.individual_id == self.related_id:
            raise ValueError(
                "An individual cannot have a relationship with themselves.")
        if self.initial_relationship == InitialRelationshipEnum.PARTNER:
            if not (self.union_date and self.union_place):
                raise ValueError(
                    "Union date and place are required for partner relationships.")
        elif self.initial_relationship in {
            InitialRelationshipEnum.CHILD,
            InitialRelationshipEnum.PARENT}:
            if self.relationship_detail_vertical:
                raise ValueError(
                    "Vertical details are invalid for parent-child relationships.")

    def __repr__(self) -> str:
        return (
            f"<Relationship(id={self.id}, individual_id={self.individual_id}, related_id={self.related_id}, "
            f"initial_relationship={self.initial_relationship}, union_date={self.union_date}, dissolution_date={self.dissolution_date})>"
        )
