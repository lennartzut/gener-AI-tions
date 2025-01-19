from flask import current_app
from flask_jwt_extended import verify_jwt_in_request, \
    get_jwt_identity
from jwt.exceptions import ExpiredSignatureError, DecodeError

from app.extensions import SessionLocal
from app.services.user_service import UserService


def inject_current_user():
    """
    Injects the current user into the template context if a valid JWT exists.

    Returns:
        dict: Dictionary containing the current user or None.
    """
    user = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            with SessionLocal() as session:
                service = UserService(db=session)
                user = service.get_user_by_id(user_id=int(user_id))
    except (ExpiredSignatureError, DecodeError):
        pass
    except Exception as e:
        current_app.logger.warning(
            f"Failed to inject current user: {e}")
    finally:
        return dict(current_user=user)
