from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, func)
from sqlalchemy.orm import relationship
from app.models.base_model import Base


class CustomEnum(Base):
    __tablename__ = 'custom_enums'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    enum_name = Column(String(50), nullable=False)  # e.g., "gender"
    enum_value = Column(String(50),
                        nullable=False)  # e.g., "non-binary"
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    # user = relationship("User", back_populates="custom_enums")

    def __repr__(self):
        return f"<CustomEnum(id={self.id}, enum_name={self.enum_name}, enum_value={self.enum_value})>"
