from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Date,
    DateTime,
    func,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.orm import relationship

from app.models.base_model import Base
from app.models.enums_model import InitialRelationshipEnum


class Individual(Base):
    """
    Represents an individual within a project.
    """

    __tablename__ = 'individuals'
    __table_args__ = (
        UniqueConstraint('project_id', 'individual_number',
                         name='uix_project_individual_number'),
        CheckConstraint(
            'death_date IS NULL OR birth_date IS NULL OR birth_date <= death_date',
            name='chk_individual_dates'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    individual_number = Column(Integer, nullable=False)
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
    project = relationship('Project', back_populates='individuals')
    identities = relationship('Identity',
                              back_populates='individual',
                              cascade='all, delete-orphan',
                              lazy='joined')
    primary_identity = relationship(
        "Identity",
        uselist=False,
        primaryjoin="and_(Individual.id == Identity.individual_id, Identity.is_primary == True)"
    )
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
        """
        Retrieves a list of parent individuals associated with this individual.

        Returns:
            list: List of dictionaries containing parent details and relationship IDs.
        """
        unique_parents = []
        seen_ids = set()

        for rel in self.relationships_as_individual:
            if rel.initial_relationship == InitialRelationshipEnum.CHILD and rel.related.id not in seen_ids:
                seen_ids.add(rel.related.id)
                unique_parents.append({
                    "id": rel.related.id,
                    "first_name": rel.related.primary_identity.first_name if rel.related.primary_identity else None,
                    "last_name": rel.related.primary_identity.last_name if rel.related.primary_identity else None,
                    "relationship_id": rel.id
                })

        for rel in self.relationships_as_related:
            if rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.individual.id not in seen_ids:
                seen_ids.add(rel.individual.id)
                unique_parents.append({
                    "id": rel.individual.id,
                    "first_name": rel.individual.primary_identity.first_name if rel.individual.primary_identity else None,
                    "last_name": rel.individual.primary_identity.last_name if rel.individual.primary_identity else None,
                    "relationship_id": rel.id
                })

        return unique_parents

    @property
    def siblings(self):
        """
        Retrieves a list of sibling individuals associated with this individual.

        Returns:
            list: List of dictionaries containing sibling details.
        """
        siblings_set = []
        seen_ids = set()
        parents = self.parents

        for parent in parents:
            parent_id = parent["id"]

            parent_obj = next(
                (rel.individual for rel in
                 self.relationships_as_related if
                 rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.individual.id == parent_id),
                None
            ) or next(
                (rel.related for rel in
                 self.relationships_as_individual if
                 rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.related.id == parent_id),
                None
            )

            if parent_obj:
                for child_rel in parent_obj.relationships_as_individual:
                    if (
                            child_rel.initial_relationship == InitialRelationshipEnum.PARENT
                            and child_rel.related.id != self.id
                            and child_rel.related.id not in seen_ids
                    ):
                        seen_ids.add(child_rel.related.id)
                        siblings_set.append({
                            "id": child_rel.related.id,
                            "first_name": child_rel.related.primary_identity.first_name if child_rel.related.primary_identity else None,
                            "last_name": child_rel.related.primary_identity.last_name if child_rel.related.primary_identity else None,
                        })

        return siblings_set

    @property
    def children(self):
        """
        Retrieves a list of child individuals associated with this individual.

        Returns:
            list: List of dictionaries containing child details and relationship IDs.
        """
        unique_children = []
        seen_ids = set()

        for rel in self.relationships_as_individual:
            if rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.related.id not in seen_ids:
                seen_ids.add(rel.related.id)
                unique_children.append({
                    "id": rel.related.id,
                    "first_name": rel.related.primary_identity.first_name if rel.related.primary_identity else None,
                    "last_name": rel.related.primary_identity.last_name if rel.related.primary_identity else None,
                    "relationship_id": rel.id
                })

        for rel in self.relationships_as_related:
            if rel.initial_relationship == InitialRelationshipEnum.CHILD and rel.individual.id not in seen_ids:
                seen_ids.add(rel.individual.id)
                unique_children.append({
                    "id": rel.individual.id,
                    "first_name": rel.individual.primary_identity.first_name if rel.individual.primary_identity else None,
                    "last_name": rel.individual.primary_identity.last_name if rel.individual.primary_identity else None,
                    "relationship_id": rel.id
                })

        return unique_children

    @property
    def partners(self):
        """
        Retrieves a list of partner individuals associated with this individual.

        Returns:
            list: List of dictionaries containing partner details and relationship IDs.
        """
        unique_partners = []
        seen_ids = set()

        for rel in self.relationships_as_individual:
            if rel.initial_relationship == InitialRelationshipEnum.PARTNER and rel.related.id not in seen_ids:
                seen_ids.add(rel.related.id)
                unique_partners.append({
                    "id": rel.related.id,
                    "first_name": rel.related.primary_identity.first_name if rel.related.primary_identity else None,
                    "last_name": rel.related.primary_identity.last_name if rel.related.primary_identity else None,
                    "relationship_id": rel.id
                })

        for rel in self.relationships_as_related:
            if rel.initial_relationship == InitialRelationshipEnum.PARTNER and rel.individual.id not in seen_ids:
                seen_ids.add(rel.individual.id)
                unique_partners.append({
                    "id": rel.individual.id,
                    "first_name": rel.individual.primary_identity.first_name if rel.individual.primary_identity else None,
                    "last_name": rel.individual.primary_identity.last_name if rel.individual.primary_identity else None,
                    "relationship_id": rel.id
                })

        return unique_partners

    @property
    def primary_identity(self):
        """
        Retrieves the primary identity associated with this individual.

        Returns:
            Identity: The primary identity object or None if not set.
        """
        return next((identity for identity in self.identities if
                     identity.is_primary), None)

    @property
    def first_name(self):
        """
        Retrieves the first name from the primary identity.

        Returns:
            str: The first name or None if primary identity is absent.
        """
        return self.primary_identity.first_name if self.primary_identity else None

    @property
    def last_name(self):
        """
        Retrieves the last name from the primary identity.

        Returns:
            str: The last name or None if primary identity is absent.
        """
        return self.primary_identity.last_name if self.primary_identity else None

    def __repr__(self) -> str:
        return (
            f"<Individual(id={self.id}, individual_number={self.individual_number}, "
            f"birth_date={self.birth_date}, birth_place='{self.birth_place}', "
            f"death_date={self.death_date}, death_place='{self.death_place}')>"
        )
