"""
User model for managing user account details and authentication.
"""

from datetime import datetime, timezone
from app.extensions import db, bcrypt


class User(db.Model):
    """
    Represents a user in the application.
    """

    __tablename__ = 'users'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(50), unique=True, nullable=False, index=True
    )
    email = db.Column(
        db.String(150), unique=True, nullable=False, index=True
    )
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    individuals = db.relationship(
        'Individual',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    # Methods
    def set_password(self, password: str) -> None:
        """
        Hashes the password using Flask-Bcrypt and stores it.

        Args:
            password (str): The plaintext password to hash.
        """
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verifies the provided password against the stored hash.

        Args:
            password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bcrypt.check_password_hash(self.password_hash,
                                          password)

    def __repr__(self) -> str:
        """
        Provides a string representation of the User instance.

        Returns:
            str: A string describing the user.
        """
        return (
            f"<User(id={self.id}, username='{self.username}', "
            f"email='{self.email}')>"
        )
