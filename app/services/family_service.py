from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.family import Family
from app.models.individual import Individual
from app.models.enums import LegalRelationshipEnum


class FamilyService:
    def __init__(self, db: Session):
        self.db = db

    def create_family(self, project_id: int, partner1_id: int,
                      partner2_id: Optional[int],
                      relationship_type: LegalRelationshipEnum,
                      union_date: Optional[str] = None,
                      union_place: Optional[str] = None) -> Family:
        """Create a new family entry."""
        new_family = Family(
            project_id=project_id,
            partner1_id=partner1_id,
            partner2_id=partner2_id,
            relationship_type=relationship_type,
            union_date=union_date,
            union_place=union_place,
        )
        self.db.add(new_family)
        self.db.commit()
        self.db.refresh(new_family)
        return new_family

    def update_family(self, family_id: int, **kwargs) -> Optional[
        Family]:
        """Update an existing family record."""
        family = self.get_family_by_id(family_id)
        if not family:
            return None

        for key, value in kwargs.items():
            if hasattr(family, key):
                setattr(family, key, value)

        self.db.commit()
        self.db.refresh(family)
        return family

    def get_family_by_id(self, family_id: int) -> Optional[Family]:
        """Retrieve a family by its ID."""
        return self.db.query(Family).filter(
            Family.id == family_id).first()

    def delete_family(self, family_id: int) -> Optional[Family]:
        """Delete a family record by its ID."""
        family = self.get_family_by_id(family_id)
        if not family:
            return None

        self.db.delete(family)
        self.db.commit()
        return family

    def add_child_to_family(self, family_id: int, child_id: int) -> \
    Optional[Family]:
        """Add a child to a family."""
        family = self.get_family_by_id(family_id)
        child = self.db.query(Individual).filter(
            Individual.id == child_id).first()

        if not family or not child:
            return None

        if child not in family.children:
            family.children.append(child)

        self.db.commit()
        self.db.refresh(family)
        return family

    def remove_child_from_family(self, family_id: int,
                                 child_id: int) -> Optional[Family]:
        """Remove a child from a family."""
        family = self.get_family_by_id(family_id)
        child = self.db.query(Individual).filter(
            Individual.id == child_id).first()

        if not family or not child:
            return None

        if child in family.children:
            family.children.remove(child)

        self.db.commit()
        self.db.refresh(family)
        return family

    def list_families_by_project(self, project_id: int) -> List[
        Family]:
        """List all families associated with a specific project."""
        return self.db.query(Family).filter(
            Family.project_id == project_id).all()

    def validate_family(self, family_id: int) -> bool:
        """Validate the integrity of a family."""
        family = self.get_family_by_id(family_id)
        if not family:
            return False

        if family.partner1_id and family.partner2_id and family.partner1_id == family.partner2_id:
            raise ValueError(
                "Partners in a family cannot be the same individual.")

        return True
