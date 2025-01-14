from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base_model import Base
from app.utils.password import hash_password, verify_password


class User(Base):
    """
    Represents a user of the application.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True,
                      index=True)
    email = Column(String(120), nullable=False, unique=True,
                   index=True)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    individuals = relationship('Individual', back_populates='user',
                               cascade='all, delete-orphan')
    projects = relationship('Project', back_populates='user',
                            cascade='all, delete-orphan')

    def set_password(self, password: str):
        """
        Hashes and sets the user's password.

        Args:
            password (str): The plain text password to hash and set.
        """
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """
        Verifies a plain text password against the stored hashed password.

        Args:
            password (str): The plain text password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return verify_password(password, self.password_hash)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}', is_admin={self.is_admin})>"
