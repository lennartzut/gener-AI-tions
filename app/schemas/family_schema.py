from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List
from datetime import date
from app.models.enums import LegalRelationshipEnum
from app.schemas.individual_schema import IndividualOut


class FamilyBase(BaseModel):
    partner1_id: int = Field(...,
                             description="ID of the first partner")
    partner2_id: Optional[int] = Field(None,
                                       description="ID of the second partner")
    relationship_type: Optional[LegalRelationshipEnum] = Field(None,
                                                               description="Type of relationship between partners")
    union_date: Optional[date] = Field(None,
                                       description="Date when the union was established")
    union_place: Optional[str] = Field(None, max_length=100,
                                       description="Place where the union was established")
    dissolution_date: Optional[date] = Field(None,
                                             description="Date when the union was dissolved, if applicable")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def validate_dates(cls, values):
        union_date = values.get('union_date')
        dissolution_date = values.get('dissolution_date')
        if union_date and dissolution_date and dissolution_date < union_date:
            raise ValueError(
                "Dissolution date cannot be earlier than union date.")
        return values


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(FamilyBase):
    pass


class FamilyOut(FamilyBase):
    id: int = Field(..., description="ID of the family")
    partner1: IndividualOut = Field(...,
                                    description="First partner in the family")
    partner2: Optional[IndividualOut] = Field(None,
                                              description="Second partner in the family")
    children_ids: List[int] = Field(default_factory=list,
                                    description="List of child IDs in the family")

    model_config = ConfigDict(from_attributes=True)
