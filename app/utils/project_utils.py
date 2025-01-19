from flask import abort

from app.services.project_service import ProjectService


def get_valid_project(user_id: int, project_id: int,
                      db_session=None):
    """
    Retrieves a project by ID and verifies ownership.

    Args:
        user_id (int): The ID of the current user.
        project_id (int): The ID of the project to retrieve.
        db_session (Session, optional): The database session to use. Defaults to None.

    Returns:
        Project: The retrieved project object.

    Raises:
        HTTPException: If the project is not found or not owned by the user.
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
