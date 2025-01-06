from functools import wraps
from flask_jwt_extended import get_jwt
from flask import jsonify


def admin_required(fn):
    """
    Decorator to require admin privileges for a route.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        jwt = get_jwt()
        if not jwt.get("is_admin", False):
            return jsonify({"error": "Admin privileges required."}), 403
        return fn(*args, **kwargs)
    return wrapper