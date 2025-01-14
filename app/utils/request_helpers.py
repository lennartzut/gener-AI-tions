from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import Unauthorized


def get_current_user_id_or_401() -> int:
    """
    Retrieves the current user's ID from the JWT token.

    Returns:
        int: The current user's ID.

    Raises:
        Unauthorized: If no valid user identity is found in the
        token or the user ID is invalid.
    """
    current_user_id = get_jwt_identity()
    if not current_user_id or not str(current_user_id).strip():
        raise Unauthorized("No user identity in token.")
    try:
        return int(current_user_id)
    except ValueError:
        raise Unauthorized("Invalid user ID in token.")
