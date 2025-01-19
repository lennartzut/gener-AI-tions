from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.source import Source


class SourceService:
    def __init__(self, SessionLocal: Session):
        self.SessionLocal = SessionLocal

    def create_source(self, title: str, author: Optional[str] = None,
                      publication_info: Optional[str] = None,
                      notes: Optional[str] = None) -> Source:
        new_source = Source(
            title=title,
            author=author,
            publication_info=publication_info,
            notes=notes
        )
        self.SessionLocal.add(new_source)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(new_source)
        return new_source

    def get_source_by_id(self, source_id: int) -> Optional[Source]:
        return self.SessionLocal.query(Source).filter(
            Source.id == source_id).first()

    def update_source(self, source_id: int, **kwargs) -> Optional[
        Source]:
        source = self.get_source_by_id(source_id)
        if not source:
            return None
        for k, v in kwargs.items():
            if hasattr(source, k):
                setattr(source, k, v)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(source)
        return source

    def delete_source(self, source_id: int) -> Optional[Source]:
        source = self.get_source_by_id(source_id)
        if source:
            self.SessionLocal.delete(source)
            self.SessionLocal.commit()
            return source
        return None

    def list_all_sources(self) -> List[Source]:
        return self.SessionLocal.query(Source).all()
