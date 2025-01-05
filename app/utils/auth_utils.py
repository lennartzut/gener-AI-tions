from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import Unauthorized, BadRequest


def validate_token_and_get_user():
    current_user_id = get_jwt_identity()
    if not current_user_id or not str(current_user_id).strip():
        raise Unauthorized("No user identity in token. Please log in.")
    try:
        return int(current_user_id)
    except ValueError:
        raise BadRequest("Invalid user ID in token.")
