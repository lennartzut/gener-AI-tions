from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, constr
from typing import Optional, List
from datetime import date
from app.models.enums import GenderEnum, LegalRelationshipEnum, \
    FamilyRelationshipEnum
from app.schemas.identity_schema import IdentityOut


# Individual Schemas
class IndividualBase(BaseModel):
    birth_date: Optional[date] = Field(None,
                                       description="Birth date of the individual")
    birth_place: Optional[
        constr(min_length=1, max_length=100)] = Field(
        None, description="Birth place of the individual"
    )
    death_date: Optional[date] = Field(None,
                                       description="Death date of the individual")
    death_place: Optional[
        constr(min_length=1, max_length=100)] = Field(
        None, description="Death place of the individual"
    )

    model_config = ConfigDict(from_attributes=True)


class IndividualCreate(IndividualBase):
    user_id: int = Field(...,
                         description="ID of the associated user")
    first_name: str = Field(..., min_length=1, max_length=50,
                            description="First name of the individual")
    last_name: str = Field(..., min_length=1, max_length=50,
                           description="Last name of the individual")
    gender: GenderEnum = Field(...,
                               description="Gender of the individual")
    valid_from: Optional[date] = Field(None,
                                       description="Validity start date for the identity")
    valid_until: Optional[date] = Field(None,
                                        description="Validity end date for the identity")


class IndividualUpdate(IndividualBase):
    pass


class IndividualOut(BaseModel):
    id: int = Field(..., description="ID of the individual")
    birth_date: Optional[date]
    birth_place: Optional[str]
    death_date: Optional[date]
    death_place: Optional[str]
    identities: List[IdentityOut] = Field(default_factory=list)
    primary_identity: Optional[IdentityOut]

    model_config = ConfigDict(from_attributes=True)


# Relationship Schemas
class RelationshipBase(BaseModel):
    parent_id: int = Field(...,
                           description="ID of the parent individual")
    child_id: int = Field(...,
                          description="ID of the child individual")
    relationship_type: FamilyRelationshipEnum = Field(...,
                                                      description="Type of relationship")

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
