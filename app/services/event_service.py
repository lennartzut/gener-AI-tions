from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.event import Event


class EventService:
    def __init__(self, SessionLocal: Session):
        self.SessionLocal = SessionLocal

    def create_event(self, entity_type: str, entity_id: int,
                     event_type: str,
                     event_date=None, event_place=None,
                     notes=None) -> Event:
        new_event = Event(
            entity_type=entity_type,
            entity_id=entity_id,
            event_type=event_type,
            event_date=event_date,
            event_place=event_place,
            notes=notes
        )
        self.SessionLocal.add(new_event)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(new_event)
        return new_event

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        return self.SessionLocal.query(Event).filter(
            Event.id == event_id).first()

    def update_event(self, event_id: int, **kwargs) -> Optional[
        Event]:
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        for k, v in kwargs.items():
            if hasattr(event, k):
                setattr(event, k, v)
        self.SessionLocal.commit()
        self.SessionLocal.refresh(event)
        return event

    def delete_event(self, event_id: int) -> Optional[Event]:
        event = self.get_event_by_id(event_id)
        if event:
            self.SessionLocal.delete(event)
            self.SessionLocal.commit()
            return event
        return None

    def list_events_for_entity(self, entity_type: str,
                               entity_id: int) -> List[Event]:
        return self.SessionLocal.query(Event).filter(
            Event.entity_type == entity_type,
            Event.entity_id == entity_id).all()
