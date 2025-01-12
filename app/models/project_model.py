from sqlalchemy import (Column, Integer, Sequence, String, DateTime, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base_model import Base


class Project(Base):
    __tablename__ = 'projects'

    project_number_seq = Sequence('project_number_seq')
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_number = Column(
        Integer,
        project_number_seq,
        nullable=False,
        unique=True
    )
    user_id = Column(Integer,
                     ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('User', back_populates='projects')
    individuals = relationship('Individual',
                               back_populates='project',
                               cascade='all, delete-orphan')
    relationships = relationship('Relationship',
                                 back_populates='project',
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    def count_related_entities(self):
        """
        Counts the number of individuals and relationships in this project.
        """
        return {
            'individuals': len(self.individuals),
            'relationships': len(self.relationships)
        }
