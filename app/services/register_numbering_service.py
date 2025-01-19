from sqlalchemy.orm import Session
from typing import Dict, List
from app.models.individual_model import Individual
from app.models.relationship import Relationship
from datetime import date


class RegisterNumberingService:
    def __init__(self, SessionLocal: Session):
        self.SessionLocal = SessionLocal

    def compute_register_numbers(self, root_individual_id: int) -> \
    Dict[int, int]:
        register_map = {}
        next_number = 2  # The root gets #1, children start at #2

        def assign_numbers(individual_id: int, current_number: int):
            register_map[individual_id] = current_number

            children = self._get_children(individual_id)
            children.sort(
                key=lambda c: (c.birth_date or date.min, c.id))

            nonlocal next_number
            for child in children:
                assign_numbers(child.id, next_number)
                next_number += 1

        assign_numbers(root_individual_id, 1)
        return register_map

    def _get_children(self, parent_id: int) -> List[Individual]:
        rels = (self.SessionLocal.query(Relationship)
                .filter(Relationship.individual_id == parent_id,
                        Relationship.relationship_type == 'parent')
                .all())

        child_ids = [r.related_id for r in rels]
        if not child_ids:
            return []

        children = self.SessionLocal.query(Individual).filter(
            Individual.id.in_(child_ids)).all()
        return children
