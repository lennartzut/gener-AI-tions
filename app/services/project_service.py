import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.project_model import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Service layer for managing projects.

    Provides methods to create, retrieve, update, and delete projects
    associated with users.
    """

    def __init__(self, db: Session):
        """
        Initializes the ProjectService with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    def create_project(self, user_id: int,
                       project_create: ProjectCreate) -> Optional[
        Project]:
        """
        Creates a new project for a user.

        Args:
            user_id (int): The ID of the user creating the project.
            project_create (ProjectCreate): The schema containing project details.

        Returns:
            Optional[Project]: The newly created Project object if successful, else None.
        """
        try:
            max_project_number = self.db.query(
                func.max(Project.project_number)) \
                .filter(Project.user_id == user_id) \
                .scalar()
            next_project_number = 1 if max_project_number is None else max_project_number + 1

            new_project = Project(
                user_id=user_id,
                project_number=next_project_number,
                name=project_create.name
            )
            self.db.add(new_project)
            self.db.commit()
            self.db.refresh(new_project)
            logger.info(f"Project created: ID={new_project.id}")
            return new_project
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Error creating project for user {user_id}: {e}")
            return None

    def get_projects_by_user(self, user_id: int) -> List[Project]:
        """
        Fetches all projects for a specific user.

        Args:
            user_id (int): The ID of the user whose projects are to be retrieved.

        Returns:
            List[Project]: A list of Project objects associated with the user.
        """
        try:
            projects = self.db.query(Project).filter(
                Project.user_id == user_id
            ).all()
            logger.info(
                f"Retrieved {len(projects)} projects for user {user_id}")
            return projects
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Error retrieving projects for user {user_id}: {e}")
            return []

    def get_project_by_id(self, project_id: int) -> Optional[
        Project]:
        """
        Fetches a project by its ID.

        Args:
            project_id (int): The unique ID of the project to retrieve.

        Returns:
            Optional[Project]: The Project object if found, else None.
        """
        try:
            project = self.db.query(Project).filter(
                Project.id == project_id).first()
            if not project:
                logger.warning(f"Project not found: ID={project_id}")
            return project
        except SQLAlchemyError as e:
            logger.error(
                f"Error retrieving project by ID {project_id}: {e}")
            return None

    def update_project(self, project_id: int, user_id: int,
                       project_update: ProjectUpdate) -> Optional[
        Project]:
        """
        Updates an existing project for a user.

        Args:
            project_id (int): The unique ID of the project to update.
            user_id (int): The ID of the user requesting the update.
            project_update (ProjectUpdate): The schema containing updated project details.

        Returns:
            Optional[Project]: The updated Project object if successful, else None.
        """
        try:
            project = self.db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            if not project:
                logger.warning(
                    f"Project not found for update: ID={project_id}, User={user_id}")
                return None

            if project_update.name:
                project.name = project_update.name

            self.db.commit()
            self.db.refresh(project)
            logger.info(f"Project updated: ID={project_id}")
            return project
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Error updating project for user {user_id}: {e}")
            return None

    def delete_project(self, project_id: int, user_id: int) -> bool:
        """
        Deletes a project by its ID.

        Args:
            project_id (int): The unique ID of the project to delete.
            user_id (int): The ID of the user requesting the deletion.

        Returns:
            bool: True if deletion was successful, else False.
        """
        try:
            project = self.db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            if not project:
                logger.warning(
                    f"Project not found for deletion: ID={project_id}, User={user_id}")
                return False

            self.db.delete(project)
            self.db.commit()
            logger.info(f"Project deleted: ID={project_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                f"Error deleting project for user {user_id}: {e}")
            return False
