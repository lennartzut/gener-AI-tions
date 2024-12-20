from sqlalchemy import (Column, Integer, String, Text, ForeignKey,
                        Date, DateTime, func)
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.associations import family_children_association_table


class Individual(Base):
    __tablename__ = 'individuals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,
                     ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False, index=True)
    project_id = Column(Integer, ForeignKey('projects.id',
                                            ondelete='CASCADE'),
                        nullable=False, index=True)

    birth_date = Column(Date, nullable=True)
    birth_place = Column(String(100), nullable=True, index=True)
    death_date = Column(Date, nullable=True)
    death_place = Column(String(100), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    user = relationship('User', back_populates='individuals')
    project = relationship('Project', back_populates='individuals',
                           foreign_keys=[project_id])

    identities = relationship('Identity',
                              back_populates='individual',
                              cascade='all, delete-orphan')

    families_as_partner1 = relationship('Family',
                                        foreign_keys='Family.partner1_id',
                                        back_populates='partner1',
                                        cascade='all, delete-orphan')
    families_as_partner2 = relationship('Family',
                                        foreign_keys='Family.partner2_id',
                                        back_populates='partner2',
                                        cascade='all, delete-orphan')

    relationships_as_individual = relationship('Relationship',
                                               foreign_keys='Relationship.individual_id',
                                               back_populates='individual',
                                               cascade='all, delete-orphan')
    relationships_as_related = relationship('Relationship',
                                            foreign_keys='Relationship.related_id',
                                            back_populates='related',
                                            cascade='all, delete-orphan')

    families = relationship('Family',
                            secondary=family_children_association_table,
                            back_populates='children')

    @property
    def primary_identity(self):
        for ident in self.identities:
            if ident.is_primary:
                return ident
        return None

    def __repr__(self):
        return f"<Individual(id={self.id}, birth_place='{self.birth_place}', birth_date={self.birth_date})>"
