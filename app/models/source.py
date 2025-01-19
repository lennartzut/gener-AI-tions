from sqlalchemy import (Column, Integer, String, DateTime, Text,
                        func)
from sqlalchemy.orm import relationship
from app.models.base_model import Base


class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=True)
    publication_info = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        onupdate=func.now(), nullable=False)

    citations = relationship('Citation', back_populates='source',
                             cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Source(id={self.id}, title='{self.title}')>"
