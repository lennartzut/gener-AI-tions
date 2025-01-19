from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class CitationBase(BaseModel):
    source_id: int = Field(...,
                           description="ID of the associated source")
    entity_type: str = Field(...,
                             description="'individual', 'family', or 'event'")
    entity_id: int = Field(...,
                           description="ID of the related entity")
    notes: Optional[str] = Field(None,
                                 description="Additional notes")

    model_config = ConfigDict(from_attributes=True)


class CitationCreate(CitationBase):
    pass


class CitationUpdate(CitationBase):
    pass


class CitationOut(CitationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
