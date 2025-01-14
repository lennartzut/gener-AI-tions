from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.exceptions import BadRequest


def validate_token_and_get_user():
    """
    Validates the JWT token and retrieves the current user's ID.

    Returns:
        int: The current user's ID.

    Raises:
        NoAuthorizationError: If no valid user identity is found
        in the token.
        BadRequest: If the user ID in the token is invalid.
    """
    current_user_id = get_jwt_identity()
    if not current_user_id or not str(current_user_id).strip():
        raise NoAuthorizationError(
            "No user identity in token. Please log in.")
    try:
        return int(current_user_id)
    except ValueError:
        raise BadRequest("Invalid user ID in token.")
