from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.models.individual import Individual
from app.models.enums import FamilyRelationshipEnum


class IndividualService:
    def __init__(self, db: Session):
        self.db = db

    def create_individual(self, user_id: int, project_id: int,
                          birth_date: Optional[date] = None,
                          birth_place: Optional[str] = None,
                          death_date: Optional[date] = None,
                          death_place: Optional[str] = None,
                          notes: Optional[str] = None) -> Individual:
        """
        Create a new individual record.
        """
        new_individual = Individual(
            user_id=user_id,
            project_id=project_id,
            birth_date=birth_date,
            birth_place=birth_place,
            death_date=death_date,
            death_place=death_place,
            notes=notes
        )
        self.db.add(new_individual)
        self.db.commit()
        self.db.refresh(new_individual)
        return new_individual

    def get_individual_by_id(self, individual_id: int) -> Optional[Individual]:
        """
        Retrieve an individual by ID.
        """
        return self.db.query(Individual).filter(Individual.id == individual_id).first()

    def update_individual(self, individual_id: int, **kwargs) -> Optional[Individual]:
        """
        Update fields of an existing individual.
        """
        individual = self.get_individual_by_id(individual_id)
        if not individual:
            return None

        for key, value in kwargs.items():
            if hasattr(individual, key):
                setattr(individual, key, value)
        self.db.commit()
        self.db.refresh(individual)
        return individual

    def delete_individual(self, individual_id: int) -> Optional[Individual]:
        """
        Fully delete an individual record.
        """
        individual = self.get_individual_by_id(individual_id)
        if not individual:
            return None

        self.db.delete(individual)
        self.db.commit()
        return individual

    def calculate_age(self, birth_date: Optional[date], death_date: Optional[date] = None) -> Optional[int]:
        """
        Calculate the age of an individual based on birth and death date.
        """
        if not birth_date:
            return None
        today = death_date or date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    def get_age(self, individual_id: int) -> Optional[int]:
        """
        Get the age of an individual using their birth_date and death_date.
        """
        individual = self.get_individual_by_id(individual_id)
        if not individual:
            return None

        return self.calculate_age(individual.birth_date, individual.death_date)

    def get_parents(self, individual_id: int) -> List[Individual]:
        """
        Get the parents of an individual based on relationships.
        relationship_type='parent' means individual_id=parent, related_id=child
        So if this person is the child, we find relationships where related_id=individual_id and type='parent'
        """
        individual = self.get_individual_by_id(individual_id)
        if not individual:
            return []
        # Using model helpers:
        return individual.get_parents()

    def get_children(self, individual_id: int, partner_id: Optional[int] = None) -> List[Individual]:
        """
        Get children of the given individual. If partner_id is provided, filter children to those belonging
        to a family with that partner.
        """
        individual = self.get_individual_by_id(individual_id)
        if not individual:
            return []

        all_children = individual.get_children()

        if partner_id:
            # If families are used to store partner-child relationships:
            # If we want only the children that belong to both individuals (like a combined family),
            # we can find a family that includes both individuals as parents and then filter children by that.
            # For now, just return all_children since the relationship model drives it.
            # If you have a family logic implemented, you can filter based on that.
            return [c for c in all_children if partner_id in [p.id for p in c.get_parents()]]
        else:
            return all_children
