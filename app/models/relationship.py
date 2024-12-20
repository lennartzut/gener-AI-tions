from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Relationship(Base):
    __tablename__ = 'relationships'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id',
                                            ondelete='CASCADE'),
                        nullable=False)
    family_id = Column(Integer,
                       ForeignKey('families.id', ondelete='CASCADE'),
                       nullable=True)

    individual_id = Column(Integer, ForeignKey('individuals.id',
                                               ondelete='CASCADE'),
                           nullable=False)
    related_id = Column(Integer, ForeignKey('individuals.id',
                                            ondelete='CASCADE'),
                        nullable=False)

    relationship_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    project = relationship('Project', back_populates='relationships')
    family = relationship('Family', back_populates='relationships',
                          foreign_keys=[family_id], uselist=False)

    individual = relationship('Individual',
                              foreign_keys=[individual_id],
                              back_populates='relationships_as_individual')
    related = relationship('Individual', foreign_keys=[related_id],
                           back_populates='relationships_as_related')

    def __repr__(self):
        return (
            f"<Relationship(id={self.id}, individual_id={self.individual_id}, "
            f"related_id={self.related_id}, type={self.relationship_type}, family_id={self.family_id})>")
