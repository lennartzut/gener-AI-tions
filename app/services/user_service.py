from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str,
                    password: str) -> User:
        """
        Create a new user with hashed password.
        """
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Fetch a user by their ID.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Fetch a user by their email.
        """
        return self.db.query(User).filter(
            User.email == email).first()

    def email_or_username_exists(self, email: str,
                                 username: str) -> bool:
        """
        Check if a user exists with the given email or username.
        """
        return self.db.query(User).filter((User.email == email) | (
                    User.username == username)).first() is not None

    def soft_delete_user(self, user_id: int) -> Optional[User]:
        """
        Soft delete a user by setting deleted_at.
        """
        user = self.get_user_by_id(user_id)
        if user:
            user.soft_delete()
            self.db.commit()
        return user

    def authenticate_user(self, email: str, password: str) -> \
    Optional[User]:
        """
        Authenticate a user by email and password.
        Returns the user if authenticated, None otherwise.
        """
        user = self.get_user_by_email(email)
        if user and user.check_password(password):
            return user
        return None
