from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import RelationshipTypeEnum


class RelationshipRequest(BaseModel):
    type: RelationshipTypeEnum = Field(
        ...,
        description="Type of relationship (e.g., parent, child, partner)"
    )
    target_id: int = Field(
        ..., gt=0,
        description="ID of the related individual (must be a positive integer)"
    )

    model_config = ConfigDict(from_attributes=True)
