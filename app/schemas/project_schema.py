from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict


class ProjectBase(BaseModel):
    name: str = Field(..., description="Name of the project")
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None,
                                description="Updated name of the project")
    model_config = ConfigDict(from_attributes=True)


class ProjectOut(ProjectBase):
    id: int = Field(..., description="ID of the project")
    user_id: int = Field(...,
                         description="ID of the user who owns this project")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")
    deleted_at: Optional[datetime] = Field(None,
                                           description="Soft deletion timestamp")
    entity_counts: Optional[Dict[str, int]] = Field(None,
                                                    description="Count of related entities")

    model_config = ConfigDict(from_attributes=True)


class ProjectWithEntities(ProjectOut):
    individuals: Optional[int] = Field(None,
                                       description="Count of individuals")
    families: Optional[int] = Field(None,
                                    description="Count of families")
    relationships: Optional[int] = Field(None,
                                         description="Count of relationships")
    model_config = ConfigDict(from_attributes=True)
