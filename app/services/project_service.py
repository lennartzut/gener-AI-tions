import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.project_model import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, user_id: int,
                       project_create: ProjectCreate) -> Optional[
        Project]:
        """
        Create a new project for a user.
        """
        try:
            new_project = Project(user_id=user_id,
                                  name=project_create.name)
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
        Fetch all projects for a specific user.
        """
        try:
            projects = self.db.query(Project).filter(
                Project.user_id == user_id).all()
            logger.info(
                f"Retrieved {len(projects)} projects for user {user_id}")
            return projects
        except SQLAlchemyError as e:
            logger.error(
                f"Error retrieving projects for user {user_id}: {e}")
            return []

    def get_project_by_id(self, project_id: int) -> Optional[
        Project]:
        """
        Fetch a project by its ID.
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
        Update an existing project for a user.
        """
        try:
            project = self.db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id).first()
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
        Delete a project by its ID.
        """
        try:
            project = self.db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id).first()
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
