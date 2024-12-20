from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,
                     ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship('User', back_populates='projects')
    individuals = relationship('Individual',
                               back_populates='project',
                               cascade='all, delete-orphan')
    families = relationship('Family', back_populates='project',
                            cascade='all, delete-orphan')
    relationships = relationship('Relationship',
                                 back_populates='project',
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    def soft_delete(self):
        """Mark the project as deleted without removing it from the database."""
        self.deleted_at = func.now()

    def count_related_entities(self):
        """Count related individuals, families, and relationships."""
        return {
            'individuals': len(self.individuals),
            'families': len(self.families),
            'relationships': len(self.relationships)
        }
