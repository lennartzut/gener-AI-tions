from functools import wraps

from flask import g, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from werkzeug.exceptions import BadRequest

from app.utils.auth_utils import get_current_user_id
from app.utils.project_utils import get_valid_project


def admin_required(fn):
    """
    Decorator to enforce admin privileges on protected routes.

    Args:
        fn (callable): The route function to decorate.

    Returns:
        callable: The wrapped function with admin check.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        jwt_data = get_jwt()
        if not jwt_data.get("is_admin", False):
            return jsonify(
                {"error": "Admin privileges required."}), 403
        return fn(*args, **kwargs)

    return wrapper


def require_project_access(fn):
    """
    Decorator that:
      1) Ensures a valid JWT is present.
      2) Retrieves the current user ID.
      3) Ensures the user has access to the project specified by 'project_id'.
      4) Stores user_id and project_id in Flask's 'g' object.
    """

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        g.user_id = get_current_user_id()
        g.project_id = request.args.get('project_id', type=int)
        if not g.project_id:
            raise BadRequest("Project ID is required.")
        get_valid_project(user_id=g.user_id, project_id=g.project_id)
        return fn(*args, **kwargs)
    return wrapper
