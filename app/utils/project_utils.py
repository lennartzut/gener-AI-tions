from flask import abort
from app.models.project import Project


def get_project_or_404(user_id: int, project_id: int) -> Project:
    project = Project.query.filter_by(id=project_id,
                                      user_id=user_id).first()
    if not project:
        abort(404,
              description="Project not found or not owned by this user.")
    return project
