import logging
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from app.models.identity_model import Identity
from app.models.individual_model import Individual
from app.models.relationship_model import Relationship
from app.models.project_model import Project
from app.schemas.individual_schema import IndividualCreate, IndividualUpdate
from app.utils.validators_utils import ValidationUtils

logger = logging.getLogger(__name__)


class IndividualService:
    def __init__(self, db: Session):
        self.db = db

    def create_individual(self, user_id: int, project_id: int, individual_create: IndividualCreate) -> Optional[Individual]:
        """
        Creates a new individual along with a primary identity in a project.
        """
        try:
            project = self.db.query(Project).filter_by(id=project_id, user_id=user_id).first()
            if not project:
                raise ValueError(f"Project {project_id} not found for user {user_id}.")

            new_individual = Individual(
                user_id=user_id,
                project_id=project_id,
                birth_date=individual_create.birth_date,
                birth_place=individual_create.birth_place,
                death_date=individual_create.death_date,
                death_place=individual_create.death_place,
                notes=individual_create.notes
            )
            self.db.add(new_individual)
            self.db.flush()

            primary_identity = Identity(
                individual_id=new_individual.id,
                first_name=individual_create.first_name,
                last_name=individual_create.last_name,
                gender=individual_create.gender,
                valid_from=individual_create.birth_date,
                is_primary=True
            )
            self.db.add(primary_identity)
            self.db.commit()

            self.db.refresh(new_individual)
            logger.info(f"Created individual with ID {new_individual.id} and primary identity {primary_identity.id}.")
            return new_individual
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while creating individual: {e}")
            return None

    def update_individual(self, individual_id: int, user_id: int, project_id: int, individual_update: IndividualUpdate) -> Optional[Individual]:
        """
        Updates an individual's details and their primary identity.
        """
        try:
            individual = self.db.query(Individual).filter_by(
                id=individual_id, user_id=user_id, project_id=project_id
            ).first()
            if not individual:
                raise ValueError(f"Individual {individual_id} not found in project {project_id}.")

            updates = individual_update.model_dump(exclude_unset=True)
            for field, value in updates.items():
                setattr(individual, field, value)

            primary_identity = individual.primary_identity
            if primary_identity:
                identity_updates = {
                    key: value for key, value in updates.items() if key in ["first_name", "last_name", "gender", "birth_date"]
                }
                for field, value in identity_updates.items():
                    if field == "birth_date":
                        primary_identity.valid_from = value
                    else:
                        setattr(primary_identity, field, value)

            ValidationUtils.validate_date_order(
                individual.birth_date, individual.death_date, "Birth date must be before death date."
            )

            self.db.commit()
            self.db.refresh(individual)
            logger.info(f"Updated individual {individual_id} in project {project_id}.")
            return individual
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while updating individual: {e}")
            return None

    def delete_individual(self, individual_id: int, user_id: int, project_id: int) -> bool:
        """
        Deletes an individual by ID.
        """
        try:
            individual = self.db.query(Individual).filter_by(
                id=individual_id, user_id=user_id, project_id=project_id
            ).first()
            if not individual:
                logger.warning(f"Individual {individual_id} not found in project {project_id}.")
                return False

            self.db.delete(individual)
            self.db.commit()
            logger.info(f"Deleted individual {individual_id} from project {project_id}.")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while deleting individual: {e}")
            return False

    def get_individuals_by_project(self, user_id: int, project_id: int, search_query: Optional[str] = None) -> List[Individual]:
        """
        Fetches individuals belonging to a project, optionally filtered by a search query.
        """
        try:
            query = self.db.query(Individual).filter_by(
                user_id=user_id, project_id=project_id).options(
                joinedload(
                    Individual.relationships_as_individual).joinedload(
                    Relationship.related),
                joinedload(
                    Individual.relationships_as_related).joinedload(
                    Relationship.individual),
                joinedload(Individual.identities)
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
            return individuals
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while retrieving individuals: {e}")
            return []

    def get_individual_by_id(self, individual_id: int, user_id: int, project_id: int) -> Optional[Individual]:
        """
        Fetches a specific individual by ID, ensuring they belong to the user and project.
        """
        try:
            individual = self.db.query(Individual).filter_by(
                id=individual_id, user_id=user_id, project_id=project_id
            ).first()
            if not individual:
                logger.warning(f"Individual {individual_id} not found.")
            return individual
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving individual {individual_id}: {e}")
            return None
