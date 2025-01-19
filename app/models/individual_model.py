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
        back_populates='primary_of_individual',
        foreign_keys='Identity.individual_id',
        primaryjoin="and_(Individual.id == Identity.individual_id, "
                    "Identity.is_primary == True)",
        overlaps = "identities, individual"
    )
    relationships_as_individual = relationship(
        'Relationship',
        foreign_keys='Relationship.individual_id',
        back_populates='individual',
        cascade='all, delete-orphan'
    )
    relationships_as_related = relationship(
        'Relationship',
        foreign_keys='Relationship.related_id',
        back_populates='related',
        cascade='all, delete-orphan'
    )

    @property
    def parents(self):
        """
        Returns a list of dictionaries for each parent of this individual.
        In canonical approach, 'parent' means:
          - The row has initial_relationship='parent'
          - The row's `related_id` == self.id (the child)
          - The row's `individual_id` is the parent's ID
        So we look in `relationships_as_related` for rel.initial_relationship == 'parent'
        """
        unique_parents = []
        seen_ids = set()

        for rel in self.relationships_as_related:
            if rel.initial_relationship == InitialRelationshipEnum.PARENT:
                parent_id = rel.individual.id
                if parent_id not in seen_ids:
                    seen_ids.add(parent_id)
                    parent_first_name = (rel.individual.primary_identity.first_name
                                         if rel.individual.primary_identity else None)
                    parent_last_name = (rel.individual.primary_identity.last_name
                                        if rel.individual.primary_identity else None)

                    unique_parents.append({
                        "id": parent_id,
                        "first_name": parent_first_name,
                        "last_name": parent_last_name,
                        "relationship_id": rel.id
                    })

        return unique_parents

    @property
    def children(self):
        """
        Returns a list of dictionaries for each child of this individual.
        In canonical approach, 'parent' means:
          - The row has initial_relationship='parent'
          - The row's `individual_id` == self.id (the parent)
          - The row's `related_id` is the child's ID
        So we look in `relationships_as_individual` for rel.initial_relationship == 'parent'
        """
        unique_children = []
        seen_ids = set()

        for rel in self.relationships_as_individual:
            if rel.initial_relationship == InitialRelationshipEnum.PARENT:
                child_id = rel.related.id
                if child_id not in seen_ids:
                    seen_ids.add(child_id)
                    child_first_name = (rel.related.primary_identity.first_name
                                        if rel.related.primary_identity else None)
                    child_last_name = (rel.related.primary_identity.last_name
                                       if rel.related.primary_identity else None)

                    unique_children.append({
                        "id": child_id,
                        "first_name": child_first_name,
                        "last_name": child_last_name,
                        "relationship_id": rel.id
                    })

        return unique_children

    @property
    def partners(self):
        """
        Returns a list of dictionaries for each partner of this individual.
        In canonical approach, 'partner' means:
          - The row has initial_relationship='partner'
          - The row's `individual_id` and `related_id` can be in either side,
            but we appear in either `relationships_as_individual` or `relationships_as_related`.
        """
        unique_partners = []
        seen_ids = set()

        for rel in self.relationships_as_individual:
            if rel.initial_relationship == InitialRelationshipEnum.PARTNER:
                partner_id = rel.related.id
                if partner_id not in seen_ids:
                    seen_ids.add(partner_id)
                    partner_first_name = (rel.related.primary_identity.first_name
                                          if rel.related.primary_identity else None)
                    partner_last_name = (rel.related.primary_identity.last_name
                                         if rel.related.primary_identity else None)
                    unique_partners.append({
                        "id": partner_id,
                        "first_name": partner_first_name,
                        "last_name": partner_last_name,
                        "relationship_id": rel.id
                    })

        for rel in self.relationships_as_related:
            if rel.initial_relationship == InitialRelationshipEnum.PARTNER:
                partner_id = rel.individual.id
                if partner_id not in seen_ids:
                    seen_ids.add(partner_id)
                    partner_first_name = (rel.individual.primary_identity.first_name
                                          if rel.individual.primary_identity else None)
                    partner_last_name = (rel.individual.primary_identity.last_name
                                         if rel.individual.primary_identity else None)
                    unique_partners.append({
                        "id": partner_id,
                        "first_name": partner_first_name,
                        "last_name": partner_last_name,
                        "relationship_id": rel.id
                    })

        return unique_partners

    @property
    def siblings(self):
        """
        Returns a list of dictionaries for each sibling of this individual.
        A sibling shares a parent with us, so:
          - We gather our parents
          - For each parent, we gather that parent's children (besides us)
        """
        siblings_set = []
        seen_ids = set()

        for parent_info in self.parents:
            parent_id = parent_info["id"]
            parent_obj = None
            for rel in self.relationships_as_related:
                if rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.individual.id == parent_id:
                    parent_obj = rel.individual
                    break
            for rel in self.relationships_as_individual:
                if rel.initial_relationship == InitialRelationshipEnum.PARENT and rel.related.id == parent_id:
                    parent_obj = rel.related
                    break

            if parent_obj:
                for child_rel in parent_obj.relationships_as_individual:
                    if (child_rel.initial_relationship == InitialRelationshipEnum.PARENT
                            and child_rel.related.id != self.id
                            and child_rel.related.id not in seen_ids):
                        seen_ids.add(child_rel.related.id)
                        child_first_name = (child_rel.related.primary_identity.first_name
                                            if child_rel.related.primary_identity else None)
                        child_last_name = (child_rel.related.primary_identity.last_name
                                           if child_rel.related.primary_identity else None)
                        siblings_set.append({
                            "id": child_rel.related.id,
                            "first_name": child_first_name,
                            "last_name": child_last_name
                        })

        return siblings_set

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
