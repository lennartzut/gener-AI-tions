from pydantic import BaseModel, Field
from typing import Literal


class RelationshipRequest(BaseModel):
    type: Literal['parent', 'child', 'partner']
    target_id: int = Field(...,
                           description="ID of the related individual")
