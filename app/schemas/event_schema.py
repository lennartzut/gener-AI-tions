from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional


class EventBase(BaseModel):
    entity_type: str = Field(...,
                             description="'individual' or 'family'")
    entity_id: int = Field(..., description="ID of the entity")
    event_type: str = Field(...,
                            description="Type of the event (e.g., BIRTH, MARRIAGE)")
    event_date: Optional[date] = Field(None,
                                       description="Date of the event")
    event_place: Optional[str] = Field(None, max_length=100,
                                       description="Place of the event")
    notes: Optional[str] = Field(None,
                                 description="Additional information about the event")

    model_config = ConfigDict(from_attributes=True)


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventOut(EventBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
