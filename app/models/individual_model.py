from sqlalchemy import Column, Integer, String, Text, ForeignKey, \
    Date, DateTime, func, UniqueConstraint, Sequence, text
from sqlalchemy.orm import relationship
from app.models.base_model import Base
from app.models.enums_model import InitialRelationshipEnum


class Individual(Base):
    __tablename__ = 'individuals'
    __table_args__ = (
        UniqueConstraint('project_id', 'number',
                         name='uix_project_number'),
    )

    id = Column(Integer, primary_key=True)
    number = Column(
        Integer,
        Sequence('individual_number_seq'),
        nullable=False,
        unique=True,
        server_default=text("nextval('individual_number_seq')")
    )
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

    # Relationships
    user = relationship('User', back_populates='individuals')
    project = relationship('Project', back_populates='individuals')
    identities = relationship('Identity',
                              back_populates='individual',
                              cascade='all, delete-orphan',
                              lazy='joined')
    relationships_as_individual = relationship(
        'Relationship', foreign_keys='Relationship.individual_id',
        back_populates='individual', cascade='all, delete-orphan'
    )
    relationships_as_related = relationship(
        'Relationship', foreign_keys='Relationship.related_id',
        back_populates='related', cascade='all, delete-orphan'
    )

    @property
    def parents(self):
        """Returns a list of parent individuals."""
        return [rel.related for rel in
                self.relationships_as_individual if
                rel.initial_relationship == InitialRelationshipEnum.CHILD]

    @property
    def children(self):
        """Returns a list of child individuals."""
        return [rel.individual for rel in
                self.relationships_as_related if
                rel.initial_relationship == InitialRelationshipEnum.PARENT]

    @property
    def partners(self):
        """Returns a list of partner individuals."""
        partners = [
            rel.related for rel in self.relationships_as_individual
            if
            rel.initial_relationship == InitialRelationshipEnum.PARTNER
        ]
        partners += [
            rel.individual for rel in self.relationships_as_related
            if
            rel.initial_relationship == InitialRelationshipEnum.PARTNER
        ]
        return partners

    @property
    def siblings(self):
        """Returns a list of sibling individuals based on shared parents."""
        siblings_set = set()
        for parent in self.parents:
            siblings_set.update(child for child in parent.children if
                                child.id != self.id)
        return list(siblings_set)

    @property
    def primary_identity(self):
        """Returns the primary identity if available."""
        return next((identity for identity in self.identities if
                     identity.is_primary), None)

    @property
    def first_name(self):
        return self.primary_identity.first_name if self.primary_identity else None

    @property
    def last_name(self):
        return self.primary_identity.last_name if self.primary_identity else None

    def __repr__(self) -> str:
        return (
            f"<Individual(id={self.id}, number={self.number}, birth_date={self.birth_date}, "
            f"birth_place='{self.birth_place}', death_date={self.death_date}, death_place='{self.death_place}')>"
        )
