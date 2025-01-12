from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    """
    Base schema for a project, including common fields.
    """
    name: str = Field(..., min_length=1, max_length=255,
                      description="Name of the project")

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.
    """
    pass


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255,
                                description="Updated name of the project")

    model_config = ConfigDict(from_attributes=True)


class ProjectOut(ProjectBase):
    """
    Schema for returning project data.
    """
    id: int = Field(..., description="The unique ID of the project")
    project_number: int = Field(...,
                        description="A unique number assigned to "
                                    "the project")
    user_id: int = Field(...,
                         description="The unique ID of the user who owns the project")
    created_at: datetime = Field(...,
                                 description="The timestamp when the project was created")
    updated_at: datetime = Field(...,
                                 description="The timestamp when the project was last updated")
    entity_counts: Optional[Dict[str, int]] = Field(
        None,
        description="Counts of related entities, such as individuals and relationships"
    )

    model_config = ConfigDict(from_attributes=True)
