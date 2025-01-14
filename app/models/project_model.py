from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base_model import Base


class Project(Base):
    """
    Represents a project managed by a user.
    """

    __tablename__ = 'projects'
    __table_args__ = (
        UniqueConstraint('user_id', 'project_number',
                         name='uix_user_project_number'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_number = Column(Integer, nullable=False)
    user_id = Column(Integer,
                     ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

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
        Counts the number of individuals and relationships within this project.

        Returns:
            dict: Dictionary containing counts of individuals and relationships.
        """
        return {
            'individuals': len(self.individuals),
            'relationships': len(self.relationships)
        }
