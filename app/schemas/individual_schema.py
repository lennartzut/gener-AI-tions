from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, List
from app.models.enums import GenderEnum
from app.schemas.identity_schema import IdentityOut


class IndividualBase(BaseModel):
    birth_date: Optional[date] = Field(None,
                                       description="Birth date of the individual")
    birth_place: Optional[str] = Field(None,
                                       description="Birth place of the individual",
                                       max_length=100)
    death_date: Optional[date] = Field(None,
                                       description="Death date of the individual")
    death_place: Optional[str] = Field(None,
                                       description="Death place of the individual",
                                       max_length=100)

    model_config = ConfigDict(from_attributes=True)


class IndividualCreate(IndividualBase):
    user_id: int = Field(...,
                         description="ID of the associated user")
    project_id: int = Field(...,
                            description="ID of the associated project")
    first_name: str = Field(..., min_length=1, max_length=50,
                            description="First name of the individual")
    last_name: str = Field(..., min_length=1, max_length=50,
                           description="Last name of the individual")
    gender: GenderEnum = Field(...,
                               description="Gender of the individual")


class IndividualUpdate(IndividualBase):
    pass


class IndividualOut(IndividualBase):
    id: int
    age: Optional[int] = Field(None,
                               description="Calculated age of the individual")
    identities: List[IdentityOut] = Field(default_factory=list,
                                          description="List of identities")

    model_config = ConfigDict(from_attributes=True)
