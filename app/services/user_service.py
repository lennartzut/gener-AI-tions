import logging
from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.utils.exceptions import UserAlreadyExistsError

logger = logging.getLogger(__name__)


class UserService:
    """
    Service layer for managing users.
    Provides methods to create, retrieve, update, and delete users,
    as well as authenticate users and check for existing credentials.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_create: UserCreate) -> Optional[User]:
        """
        Creates a new user if the username and email are unique.
        """
        try:
            if self.email_or_username_exists(user_create.email,
                                             user_create.username):
                raise UserAlreadyExistsError(
                    "Email or username already in use.",
                    field="email or username")

            new_user = User(username=user_create.username,
                            email=user_create.email)
            new_user.set_password(user_create.password)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            logger.info(
                f"User created successfully: ID={new_user.id}")
            return new_user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            return None
        except UserAlreadyExistsError as e:
            logger.warning(f"User already exists: {e.field}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Fetches a user by their ID.
        """
        try:
            user = self.db.query(User).filter(
                User.id == user_id).first()
            if not user:
                logger.warning(f"User not found: ID={user_id}")
            return user
        except SQLAlchemyError as e:
            logger.error(
                f"Error retrieving user by ID {user_id}: {e}")
            return None

    def update_user(self, user_id: int, user_update: UserUpdate) -> \
    Optional[User]:
        """
        Updates user details if the email or username is not already in use.
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.warning(
                    f"User not found for update: ID={user_id}")
                return None

            if user_update.username and user_update.username != user.username:
                if self.db.query(User).filter(
                        User.username == user_update.username,
                        User.id != user_id).first():
                    raise UserAlreadyExistsError(
                        "Username already in use.", field="username")
                user.username = user_update.username

            if user_update.email and user_update.email != user.email:
                if self.db.query(User).filter(
                        User.email == user_update.email,
                        User.id != user_id).first():
                    raise UserAlreadyExistsError(
                        "Email already in use.", field="email")
                user.email = user_update.email

            if user_update.password:
                user.set_password(user_update.password)

            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User updated successfully: ID={user_id}")
            return user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating user: {e}")
            return None
        except UserAlreadyExistsError as e:
            logger.warning(f"User update failed: {e.field}")
            return None

    def delete_user(self, user_id: int) -> bool:
        """
        Deletes a user by their ID.
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.warning(
                    f"User not found for deletion: ID={user_id}")
                return False

            self.db.delete(user)
            self.db.commit()
            logger.info(f"User deleted successfully: ID={user_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting user: {e}")
            return False

    def authenticate_user(self, email: str, password: str) -> \
    Optional[User]:
        """
        Authenticates a user by email and password.
        """
        try:
            user = self.db.query(User).filter(
                User.email == email).first()
            if user and user.check_password(password):
                logger.info(
                    f"User authenticated successfully: Email={email}")
                return user
            logger.warning(f"Invalid credentials for email: {email}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def email_or_username_exists(self, email: str,
                                 username: str) -> bool:
        """
        Checks if a username or email is already in use.
        """
        try:
            return (
                    self.db.query(User)
                    .filter(or_(User.email == email,
                                User.username == username))
                    .first() is not None
            )
        except SQLAlchemyError as e:
            logger.error(
                f"Error checking email/username existence: {e}")
            return False

    def get_all_users(self) -> List[User]:
        """
        Fetches all users.
        """
        try:
            users = self.db.query(User).all()
            logger.info(
                f"Retrieved all users successfully. Count: {len(users)}")
            return users
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error retrieving all users: {e}")
            return []

    def get_paginated_users(self, page: int, per_page: int) -> List[
        User]:
        """
        Fetches a paginated list of users.
        """
        try:
            query = self.db.query(User)
            users = query.offset((page - 1) * per_page).limit(
                per_page).all()
            return users
        except SQLAlchemyError as e:
            logger.error(f"Error fetching paginated users: {e}")
            return []
