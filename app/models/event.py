from sqlalchemy import (Column, Integer, String, Date, DateTime,
                        Text, func)
from app.models.base_model import Base


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(20), nullable=False)  # 'individual' or 'family'
    entity_id = Column(Integer, nullable=False)       # ID of the entity
    event_type = Column(String(50), nullable=False)
    event_date = Column(Date, nullable=True)
    event_place = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Event(id={self.id}, entity_type={self.entity_type}, entity_id={self.entity_id}, event_type={self.event_type})>"