from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date
from app.schemas.enums import RelationshipTypeEnumRelationship
from app.schemas import UserOut


class FamilyBase(BaseModel):
    partner1_id: int = Field(...,
                             description="ID of the first partner")
    partner2_id: int = Field(...,
                             description="ID of the second partner")
    relationship_type: Optional[RelationshipTypeEnumRelationship] = Field(None,
                                                              description="Type of relationship between partners")
    union_date: Optional[date] = Field(None,
                                       description="Date when the union was established")
    union_place: Optional[str] = Field(None, max_length=100,
                                       description="Place where the union was established")
    dissolution_date: Optional[date] = Field(None,
                                             description="Date when the union was dissolved, if applicable")

    model_config = ConfigDict(from_attributes=True)


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(FamilyBase):
    pass


class FamilyOut(FamilyBase):
    id: int = Field(..., description="ID of the family")
    partner1: UserOut = Field(...,
                                    description="First partner in the family")
    partner2: UserOut = Field(...,
                                    description="Second partner in the family")

    model_config = ConfigDict(from_attributes=True)


# After all schemas are defined, rebuild to resolve forward references
FamilyOut.model_rebuild()
