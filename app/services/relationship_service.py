from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.relationship import Relationship
from app.models.individual import Individual
from app.models.enums import FamilyRelationshipEnum


class RelationshipService:
    def __init__(self, db: Session):
        self.db = db

    def create_relationship(self, project_id: int,
                            individual_id: int, related_id: int,
                            relationship_type: str) -> Relationship:
        """
        Create a new relationship entry.
        Uses 'individual_id' and 'related_id' where:
        - If relationship_type='parent': individual_id=parent, related_id=child
        - If relationship_type='child': individual_id=child, related_id=parent
        - If relationship_type='partner': individual_id=partner1, related_id=partner2
        """

        new_relationship = Relationship(
            project_id=project_id,
            family_id=None,
            individual_id=individual_id,
            related_id=related_id,
            relationship_type=relationship_type
        )
        new_relationship.validate_relationship()

        self.db.add(new_relationship)
        self.db.commit()
        self.db.refresh(new_relationship)
        return new_relationship

    def update_relationship(self, relationship_id: int, **kwargs) -> Optional[Relationship]:
        """Update an existing relationship record."""
        relationship = self.get_relationship_by_id(relationship_id)
        if not relationship:
            return None

        for key, value in kwargs.items():
            if hasattr(relationship, key):
                setattr(relationship, key, value)

        relationship.validate_relationship()

        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def delete_relationship(self, relationship_id: int) -> Optional[Relationship]:
        """Delete a relationship record by its ID."""
        relationship = self.get_relationship_by_id(relationship_id)
        if not relationship:
            return None

        self.db.delete(relationship)
        self.db.commit()
        return relationship

    def get_relationship_by_id(self, relationship_id: int) -> Optional[Relationship]:
        """Retrieve a relationship by its ID."""
        return self.db.query(Relationship).filter(Relationship.id == relationship_id).first()

    def list_relationships_by_project(self, project_id: int) -> List[Relationship]:
        """List all relationships associated with a specific project."""
        return self.db.query(Relationship).filter(
            Relationship.project_id == project_id
        ).all()

    def get_descendants(self, individual_id: int) -> List[Individual]:
        """
        Fetch all descendants of an individual.
        Descendants are found by following 'parent' relationships where this individual is the parent.
        """
        individual = self.db.query(Individual).filter(Individual.id == individual_id).first()
        if not individual:
            return []

        descendants = []
        # Children: relationship_type='parent', individual_id=this individual => related_id=child
        children = [rel.related for rel in individual.relationships_as_individual
                    if rel.relationship_type == FamilyRelationshipEnum.PARENT.value]
        for child in children:
            descendants.append(child)
            descendants.extend(self.get_descendants(child.id))
        return descendants

    def get_ancestors(self, individual_id: int) -> List[Individual]:
        """
        Fetch all ancestors of an individual.
        Ancestors are found by following 'parent' relationships where this individual is the child.
        """
        individual = self.db.query(Individual).filter(Individual.id == individual_id).first()
        if not individual:
            return []

        ancestors = []
        # Parents: relationship_type='parent', related_id=this individual => individual_id=parent
        parents = [rel.individual for rel in individual.relationships_as_related
                   if rel.relationship_type == FamilyRelationshipEnum.PARENT.value]
        for parent in parents:
            ancestors.append(parent)
            ancestors.extend(self.get_ancestors(parent.id))
        return ancestors

    def is_cyclic(self, individual_id: int, related_id: int) -> bool:
        """
        Check if adding a relationship creates a cyclic dependency.
        For a cycle: if we consider 'parent' relationships, a cycle means that 'related_id' is somehow
        an ancestor of 'individual_id'. If we add a parent relationship (individual_id=parent, related_id=child),
        then 'related_id' (child) shouldn't lead back to 'individual_id' as its ancestor.
        """
        visited = set()

        def check_cycle(curr_id: int) -> bool:
            if curr_id in visited:
                return True
            visited.add(curr_id)
            ind = self.db.query(Individual).filter(Individual.id == curr_id).first()
            if not ind:
                return False
            # Children of this 'parent':
            children = [r.related.id for r in ind.relationships_as_individual
                        if r.relationship_type == FamilyRelationshipEnum.PARENT.value]
            for child_id in children:
                if child_id == individual_id:  # cycle found
                    return True
                if check_cycle(child_id):
                    return True
            visited.remove(curr_id)
            return False

        return check_cycle(related_id)
