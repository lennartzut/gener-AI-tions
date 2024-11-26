from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, \
    check_password_hash
from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    avatar = Column(String(255),
                    nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    individuals = relationship('Individual', back_populates='user')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
