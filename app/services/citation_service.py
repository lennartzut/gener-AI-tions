from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.citation import Citation


class CitationService:
    def __init__(self, SessionLocal: Session):
        self.SessionLocal = SessionLocal

    def create_citation(self, source_id: int, entity_type: str,
                        entity_id: int,
                        notes: Optional[str] = None) -> Citation:
        new_citation = Citation(
            source_id=source_id,
            entity_type=entity_type,
            entity_id=entity_id,
            notes=notes
        )
        self.SessionLocal.add(new_citation)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(new_citation)
        return new_citation

    def get_citation_by_id(self, citation_id: int) -> Optional[
        Citation]:
        return self.SessionLocal.query(Citation).filter(
            Citation.id == citation_id).first()

    def update_citation(self, citation_id: int, **kwargs) -> \
    Optional[Citation]:
        citation = self.get_citation_by_id(citation_id)
        if not citation:
            return None
        for k, v in kwargs.items():
            if hasattr(citation, k):
                setattr(citation, k, v)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(citation)
        return citation

    def delete_citation(self, citation_id: int) -> Optional[
        Citation]:
        citation = self.get_citation_by_id(citation_id)
        if citation:
            self.SessionLocal.delete(citation)
            self.SessionLocal.commit()
            return citation
        return None

    def list_citations_for_entity(self, entity_type: str,
                                  entity_id: int) -> List[Citation]:
        return self.SessionLocal.query(Citation).filter(
            Citation.entity_type == entity_type,
            Citation.entity_id == entity_id).all()
