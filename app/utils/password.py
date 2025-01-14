from app.utils.bcrypt import bcrypt


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