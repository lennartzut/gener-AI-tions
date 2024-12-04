from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from datetime import date
from app.models.enums import RelationshipTypeEnum
from app.schemas.user_schema import UserOut


class FamilyBase(BaseModel):
    partner1_id: int = Field(...,
                             description="ID of the first partner")
    partner2_id: Optional[int] = Field(None,
                                       description="ID of the second partner")
    relationship_type: Optional[RelationshipTypeEnum] = Field(None,
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
    partner1: UserOut = Field(...,
                              description="First partner in the family")
    partner2: Optional[UserOut] = Field(None,
                                        description="Second partner in the family")
    duration: Optional[int] = Field(None,
                                    description="Duration of the union in years")

    @property
    def duration(self):
        if self.union_date and self.dissolution_date:
            return (
                        self.dissolution_date - self.union_date).days // 365
        elif self.union_date:
            return (date.today() - self.union_date).days // 365
        return None


# Resolve forward references
FamilyOut.model_rebuild()
