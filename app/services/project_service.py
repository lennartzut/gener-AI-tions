from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.project import Project


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, user_id: int, name: str) -> Project:
        """Creates a new project."""
        new_project = Project(user_id=user_id, name=name)
        self.db.add(new_project)
        self.db.commit()
        self.db.refresh(new_project)
        return new_project

    def get_project_by_id(self, project_id: int) -> Optional[
        Project]:
        """Fetches a project by its ID."""
        return self.db.query(Project).filter(
            Project.id == project_id).first()

    def get_projects_by_user(self, user_id: int) -> List[Project]:
        """Fetches all projects for a given user."""
        return (self.db.query(Project)
                .filter(Project.user_id == user_id,
                        Project.deleted_at.is_(None))
                .all())

    def update_project(self, project_id: int, name: str) -> Optional[
        Project]:
        """Updates a project's name."""
        project = self.get_project_by_id(project_id)
        if project and project.deleted_at is None:
            project.name = name
            self.db.commit()
            self.db.refresh(project)
            return project
        return None

    def soft_delete_project(self, project_id: int) -> Optional[
        Project]:
        """Soft deletes a project."""
        project = self.get_project_by_id(project_id)
        if project and project.deleted_at is None:
            project.soft_delete()
            self.db.commit()
            return project
        return None

    def count_project_entities(self, project_id: int):
        """Counts related individuals, families, and relationships."""
        project = self.get_project_by_id(project_id)
        if project:
            return project.count_related_entities()
        return None
