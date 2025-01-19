from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, Text, func)
from sqlalchemy.orm import relationship
from app.models.base_model import Base


class Citation(Base):
    __tablename__ = 'citations'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer,
                       ForeignKey('sources.id', ondelete='CASCADE'),
                       nullable=False)
    entity_type = Column(String(20),
                         nullable=False)  # 'individual', 'family', 'event'
    entity_id = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    source = relationship('Source', back_populates='citations')

    def __repr__(self):
        return f"<Citation(id={self.id}, source_id={self.source_id}, entity_type={self.entity_type}, entity_id={self.entity_id})>"
