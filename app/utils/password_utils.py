from app.utils.bcrypt_util import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    return bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    """
    return bcrypt.check_password_hash(hashed, password)