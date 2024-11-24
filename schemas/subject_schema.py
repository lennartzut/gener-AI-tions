from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List


# Identity Schemas
class IdentityBase(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    gender: Optional[str]
    valid_from: Optional[date]
    valid_until: Optional[date]


class IdentityCreate(IdentityBase):
    individual_id: int = Field(...,
                               description="ID of the associated individual")


class IdentityUpdate(IdentityBase):
    pass


class IdentityOut(IdentityBase):
    id: int
    individual_id: int

    model_config = ConfigDict(from_attributes=True)


# Individual Schemas
class IndividualBase(BaseModel):
    birth_date: Optional[date] = Field(None,
                                       description="Birth date of the individual")
    birth_place: Optional[str] = Field(None,
                                       description="Birth place of the individual")
    death_date: Optional[date] = Field(None,
                                       description="Death date of the individual")
    death_place: Optional[str] = Field(None,
                                       description="Death place of the individual")


class IndividualCreate(IndividualBase):
    pass


class IndividualUpdate(IndividualBase):
    pass


class IndividualOut(IndividualBase):
    id: int = Field(..., description="ID of the individual")
    parents: List['IndividualOut'] = Field(default_factory=list)
    siblings: List['IndividualOut'] = Field(default_factory=list)
    partners: List['IndividualOut'] = Field(default_factory=list)
    children: List['IndividualOut'] = Field(default_factory=list)
    identities: List[IdentityOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# Rebuild models to resolve forward references
IndividualOut.model_rebuild()
