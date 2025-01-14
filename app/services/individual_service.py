import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from app.models.identity_model import Identity
from app.models.individual_model import Individual
from app.models.relationship_model import Relationship
from app.schemas.individual_schema import IndividualCreate, \
    IndividualUpdate

logger = logging.getLogger(__name__)


class IndividualService:
    def __init__(self, db: Session):
        self.db = db

    def create_individual(self, user_id: int, project_id: int,
                          individual_create: IndividualCreate) -> Optional[Individual]:
        """
        Creates a new individual and a primary identity within the project.
        """
        try:
            max_individual_number = self.db.query(func.max(Individual.individual_number)) \
                .filter_by(user_id=user_id, project_id=project_id) \
                .scalar()
            next_individual_number = 1 if max_individual_number is None else max_individual_number + 1

            new_individual = Individual(
                user_id=user_id,
                project_id=project_id,
                individual_number=next_individual_number,
                **individual_create.model_dump(
                    exclude={"first_name", "last_name", "gender"})
            )
            self.db.add(new_individual)
            self.db.flush()

            # Create the primary identity
            primary_identity = Identity(
                individual_id=new_individual.id,
                first_name=individual_create.first_name,
                last_name=individual_create.last_name,
                gender=individual_create.gender,
                valid_from=individual_create.birth_date,
                is_primary=True
            )

            # Determine the next identity_number (per individual).
            max_identity_number = self.db.query(func.max(Identity.identity_number)) \
                .filter(Identity.individual_id == new_individual.id) \
                .scalar()
            next_identity_number = 1 if max_identity_number is None else max_identity_number + 1
            primary_identity.identity_number = next_identity_number

            self.db.add(primary_identity)
            self.db.commit()
            self.db.refresh(new_individual)
            logger.info(f"Created individual: ID={new_individual.id}")
            return new_individual
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during Individual creation: {e}")
            if "chk_individual_dates" in str(e).lower():
                raise ValueError("Birth date must be before death date.")
            raise e
        except ValueError as ve:
            logger.error(f"ValueError raised in IndividualService: {ve}")
            raise ve

    def get_individual_by_id(self, individual_id: int, user_id: int,
                             project_id: int) -> Optional[Individual]:
        """
        Fetches an individual by ID within the specified project.
        """
        try:
            individual = self.db.query(Individual).filter_by(
                id=individual_id, user_id=user_id,
                project_id=project_id
            ).options(
                joinedload(Individual.identities),
                joinedload(Individual.relationships_as_individual).joinedload(
                    Relationship.related),
                joinedload(Individual.relationships_as_related).joinedload(
                    Relationship.individual),
            ).first()
            if not individual:
                logger.warning(f"Individual not found: ID={individual_id}")
            return individual
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving individual by ID {individual_id}: {e}")
            return None

    def get_individuals_by_project(self, user_id: int,
                                   project_id: int,
                                   search_query: Optional[str] = None) -> List[Individual]:
        """
        Fetches all individuals in a project, optionally filtered by a search query.
        """
        try:
            query = self.db.query(Individual).filter_by(
                user_id=user_id, project_id=project_id
            ).options(
                joinedload(Individual.identities),
                joinedload(Individual.relationships_as_individual).joinedload(
                    Relationship.related),
                joinedload(Individual.relationships_as_related).joinedload(
                    Relationship.individual),
            )
            if search_query:
                search = f"%{search_query}%"
                query = query.join(Individual.identities).filter(
                    (Identity.first_name.ilike(search)) |
                    (Identity.last_name.ilike(search)) |
                    (Individual.birth_place.ilike(search))
                )

            individuals = query.order_by(
                Individual.updated_at.desc()).all()
            logger.info(f"Retrieved {len(individuals)} individuals for project {project_id}")
            return individuals
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving individuals for project {project_id}: {e}")
            return []

    def update_individual(self, individual_id: int, user_id: int,
                          project_id: int,
                          individual_update: IndividualUpdate) -> Optional[Individual]:
        """
        Updates an individual's details, including their primary identity.
        """
        try:
            individual = self.db.query(Individual).filter_by(
                id=individual_id, user_id=user_id,
                project_id=project_id
            ).first()
            if not individual:
                logger.warning(f"Individual not found for update: ID={individual_id}")
                return None

            updates = individual_update.model_dump(exclude_unset=True)
            for field, value in updates.items():
                if field in {"birth_date", "death_date",
                             "birth_place", "death_place", "notes"}:
                    setattr(individual, field, value)

            primary_identity = individual.primary_identity
            if primary_identity:
                identity_updates = {
                    key: val for key, val in updates.items()
                    if key in {"first_name", "last_name", "gender"}
                }
                for field, value in identity_updates.items():
                    setattr(primary_identity, field, value)

                if "birth_date" in updates:
                    primary_identity.valid_from = updates["birth_date"]

            self.db.commit()
            self.db.refresh(individual)
            logger.info(f"Updated individual: ID={individual_id}")
            return individual
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating individual: {e}")
            return None

    def delete_individual(self, individual_id: int, user_id: int,
                          project_id: int) -> bool:
        """
        Deletes an individual by ID.
        """
        try:
            individual = self.db.query(Individual).filter_by(
                id=individual_id, user_id=user_id,
                project_id=project_id
            ).first()
            if not individual:
                logger.warning(f"Individual not found for deletion: ID={individual_id}")
                return False

            self.db.delete(individual)
            self.db.commit()
            logger.info(f"Deleted individual: ID={individual_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting individual: {e}")
            return False
