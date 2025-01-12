from flask import abort
from app.services.project_service import ProjectService


def get_project_or_404(user_id: int, project_id: int,
                       db_session=None):
    """
    Helper to retrieve a project by ID and confirm ownership.
    Aborts with 404 if not found or not owned by user.
    """
    if db_session is None:
        from app.extensions import SessionLocal
        db_session = SessionLocal()
    service_project = ProjectService(db=db_session)
    project = service_project.get_project_by_id(
        project_id=project_id)
    if not project or project.user_id != user_id:
        abort(404,
              description="Project not found or not owned by the user.")
    return project
