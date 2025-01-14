from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt


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
        jwt = get_jwt()
        if not jwt.get("is_admin", False):
            return jsonify(
                {"error": "Admin privileges required."}), 403
        return fn(*args, **kwargs)

    return wrapper
