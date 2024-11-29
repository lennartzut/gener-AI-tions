from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date
from app.schemas.enums import GenderEnum, RelationshipType
from app.schemas.identity_schema import IdentityOut


# Individual Schemas

class IndividualBase(BaseModel):
    birth_date: Optional[date] = Field(
        None, description="Birth date of the individual"
    )
    birth_place: Optional[str] = Field(
        None, max_length=100,
        description="Birth place of the individual"
    )
    death_date: Optional[date] = Field(
        None, description="Death date of the individual"
    )
    death_place: Optional[str] = Field(
        None, max_length=100,
        description="Death place of the individual"
    )

    model_config = ConfigDict(from_attributes=True)


class IndividualCreate(IndividualBase):
    user_id: int = Field(
        ..., description="ID of the associated user"
    )


class IndividualUpdate(IndividualBase):
    pass


class IndividualOut(IndividualBase):
    id: int = Field(..., description="ID of the individual")
    parents: List[IndividualOut] = Field(
        default_factory=list, description="Parents of the individual"
    )
    siblings: List[IndividualOut] = Field(
        default_factory=list,
        description="Siblings of the individual"
    )
    partners: List[IndividualOut] = Field(
        default_factory=list,
        description="Partners of the individual"
    )
    children: List[IndividualOut] = Field(
        default_factory=list,
        description="Children of the individual"
    )
    identities: List[IdentityOut] = Field(
        default_factory=list,
        description="Identities of the individual"
    )

    model_config = ConfigDict(from_attributes=True)


# Relationship Schemas

class RelationshipBase(BaseModel):
    parent_id: int = Field(
        ..., description="ID of the parent individual"
    )
    child_id: int = Field(
        ..., description="ID of the child individual"
    )
    relationship_type: RelationshipType = Field(
        ..., description="Type of relationship"
    )

    model_config = ConfigDict(from_attributes=True)


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipUpdate(RelationshipBase):
    pass


class RelationshipOut(RelationshipBase):
    id: int = Field(..., description="ID of the relationship")
    parent: IndividualOut = Field(...,
                                  description="Parent individual")
    child: IndividualOut = Field(..., description="Child individual")

    model_config = ConfigDict(from_attributes=True)


# Resolve forward references
RelationshipOut.update_forward_refs()
IndividualOut.update_forward_refs()
