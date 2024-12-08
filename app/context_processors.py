from flask import current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
from jwt.exceptions import ExpiredSignatureError, DecodeError


def inject_current_user():
    """
    Injects the current user into the template context if a valid JWT exists.
    """
    user = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id is not None:
            user = User.query.get(int(user_id))
    except (ExpiredSignatureError, DecodeError):
        # Expected token errors
        pass
    except Exception as e:
        current_app.logger.warning(f"Failed to inject current user: {e}")
    finally:
        return dict(current_user=user)
