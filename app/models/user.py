from datetime import datetime, timezone
from app.extensions import db, bcrypt


class User(db.Model):
    """
    User model for storing user account details.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
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
    individuals = db.relationship('Individual',
                                  back_populates='user',
                                  cascade='all, delete-orphan')

    def set_password(self, password: str):
        """
        Hashes the password using Flask-Bcrypt and stores it.
        """
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Checks the hashed password against the provided password.
        """
        return bcrypt.check_password_hash(self.password_hash,
                                          password)

    def __repr__(self):
        """
        Returns a string representation of the User instance.
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
