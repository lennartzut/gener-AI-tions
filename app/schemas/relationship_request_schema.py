from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class RelationshipRequest(BaseModel):
    type: Literal['parent', 'guardian', 'child'] = Field(..., description="Type of relationship")
    target_id: int = Field(..., description="ID of the related individual")

    model_config = ConfigDict(from_attributes=True)
