from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.exceptions import BadRequest

bcrypt = Bcrypt()


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return bcrypt.generate_password_hash(password).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies a plain text password against a hashed password.

    Args:
        password (str): The plain text password to verify.
        hashed (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.check_password_hash(hashed, password)


def get_current_user_id() -> int:
    """
    Validates the JWT token and retrieves the current user's ID.

    Returns:
        int: The current user's ID.

    Raises:
        NoAuthorizationError: If no valid user identity is found in the token.
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
