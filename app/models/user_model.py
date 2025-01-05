from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base_model import Base
from app.utils.password_utils import hash_password, verify_password


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True,
                      index=True)
    email = Column(String(120), nullable=False, unique=True,
                   index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    # Relationships
    individuals = relationship('Individual', back_populates='user',
                               cascade='all, delete-orphan')
    projects = relationship('Project', back_populates='user',
                            cascade='all, delete-orphan')

    def set_password(self, password: str):
        """Hashes and sets the user's password."""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Verifies a plaintext password against the hashed password."""
        return verify_password(password, self.password_hash)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
