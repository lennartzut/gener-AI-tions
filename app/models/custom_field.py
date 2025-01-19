from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, func, Text)
from sqlalchemy.orm import relationship
from app.models.base_model import Base


class CustomField(Base):
    __tablename__ = 'custom_fields'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    table_name = Column(String(50), nullable=False)
    field_name = Column(String(50), nullable=False)
    field_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    values = relationship("CustomFieldValue",
                          back_populates="custom_field",
                          cascade='all, delete-orphan')
    # user = relationship("User", back_populates="custom_fields")

    def __repr__(self):
        return f"<CustomField(id={self.id}, table_name={self.table_name}, field_name={self.field_name}, field_type={self.field_type})>"


class CustomFieldValue(Base):
    __tablename__ = 'custom_field_values'

    id = Column(Integer, primary_key=True)
    custom_field_id = Column(Integer, ForeignKey('custom_fields.id'),
                             nullable=False)
    record_id = Column(Integer, nullable=False)
    value = Column(Text, nullable=True)

    custom_field = relationship("CustomField",
                                back_populates="values")

    def __repr__(self):
        return f"<CustomFieldValue(id={self.id}, custom_field_id={self.custom_field_id}, record_id={self.record_id})>"
