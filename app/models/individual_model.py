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
        """Returns a list of parent individuals with relationship IDs."""
        unique_parents = []
        seen_ids = set()

        # As a child
        for rel in self.relationships_as_individual:
            if rel.initial_relationship == InitialRelationshipEnum.CHILD and rel.related.id not in seen_ids:
                seen_ids.add(rel.related.id)
                unique_parents.append({
                    "id": rel.related.id,
                    "first_name": rel.related.primary_identity.first_name if rel.related.primary_identity else None,
                    "last_name": rel.related.primary_identity.last_name if rel.related.primary_identity else None,
                    "relationship_id": rel.id
                })

        # As a related individual in a parent-to-child relationship
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
        """Returns a list of sibling individuals without additional relationship IDs."""
        siblings_set = []
        seen_ids = set()

        # Collect parent IDs
        parents = self.parents  # List of dicts with parent details

        for parent in parents:
            parent_id = parent["id"]

            # Retrieve the parent Individual object from relationships_as_related
            parent_obj = next(
                (
                    rel.individual for rel in
                self.relationships_as_related
                    if
                rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.individual.id == parent_id
                ),
                None
            )

            if not parent_obj:
                # If not found in relationships_as_related, check relationships_as_individual
                parent_obj = next(
                    (
                        rel.related for rel in
                    self.relationships_as_individual
                        if
                    rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.related.id == parent_id
                    ),
                    None
                )

            if parent_obj:
                # Find all children of the parent, excluding self
                for child_rel in parent_obj.relationships_as_individual:
                    if (
                            child_rel.initial_relationship == InitialRelationshipEnum.PARENT  # Parent-to-child relationship
                            and child_rel.related.id != self.id  # Exclude self
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
        """Returns a list of child individuals with relationship IDs."""
        unique_children = []
        seen_ids = set()

        # As a parent
        for rel in self.relationships_as_individual:
            if rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.related.id not in seen_ids:
                seen_ids.add(rel.related.id)
                unique_children.append({
                    "id": rel.related.id,
                    "first_name": rel.related.primary_identity.first_name if rel.related.primary_identity else None,
                    "last_name": rel.related.primary_identity.last_name if rel.related.primary_identity else None,
                    "relationship_id": rel.id
                })

        # As a related individual in a child-to-parent relationship
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
        """Returns a list of partner individuals with relationship IDs."""
        unique_partners = []
        seen_ids = set()

        # Stored PARTNER relationships
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

        # Dynamically inferred partners (via shared children)
        for child in self.children:
            # Determine how the child is related (as a parent or child)
            child_obj = None
            # Search in relationships_as_individual
            for rel in self.relationships_as_individual:
                if rel.related.id == child["id"]:
                    child_obj = rel.related
                    break
            # If not found, search in relationships_as_related
            if not child_obj:
                for rel in self.relationships_as_related:
                    if rel.individual.id == child["id"]:
                        child_obj = rel.individual
                        break

            if child_obj:
                # Find all parents of the child except self
                for parent_rel in child_obj.relationships_as_related:
                    if (
                            parent_rel.initial_relationship == InitialRelationshipEnum.PARENT
                            and parent_rel.individual.id != self.id
                    ):
                        other_parent = parent_rel.individual
                        if other_parent.id not in seen_ids:
                            # Check for existing PARTNER relationship
                            existing_partner_rel = next(
                                (
                                    rel for rel in
                                self.relationships_as_individual
                                    if
                                rel.initial_relationship == InitialRelationshipEnum.PARTNER
                                and rel.related.id == other_parent.id
                                ),
                                None
                            )
                            relationship_id = existing_partner_rel.id if existing_partner_rel else None
                            seen_ids.add(other_parent.id)
                            unique_partners.append({
                                "id": other_parent.id,
                                "first_name": other_parent.primary_identity.first_name if other_parent.primary_identity else None,
                                "last_name": other_parent.primary_identity.last_name if other_parent.primary_identity else None,
                                "relationship_id": relationship_id
                            })

        return unique_partners

    @property
    def primary_identity(self):
        """Returns the primary identity if available."""
        return next((identity for identity in self.identities if
                     identity.is_primary), None)

    @property
    def first_name(self):
        """Returns the first name from the primary identity."""
        return self.primary_identity.first_name if self.primary_identity else None

    @property
    def last_name(self):
        """Returns the last name from the primary identity."""
        return self.primary_identity.last_name if self.primary_identity else None

    def __repr__(self) -> str:
        return (
            f"<Individual(id={self.id}, number={self.number}, birth_date={self.birth_date}, "
            f"birth_place='{self.birth_place}', death_date={self.death_date}, death_place='{self.death_place}')>"
        )
