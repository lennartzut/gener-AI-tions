from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class SourceBase(BaseModel):
    title: str = Field(..., description="Title of the source")
    author: Optional[str] = Field(None,
                                  description="Author of the source")
    publication_info: Optional[str] = Field(None,
                                            description="Publication information")
    notes: Optional[str] = Field(None,
                                 description="Additional notes")

    model_config = ConfigDict(from_attributes=True)


class SourceCreate(SourceBase):
    pass


class SourceUpdate(SourceBase):
    pass


class SourceOut(SourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
