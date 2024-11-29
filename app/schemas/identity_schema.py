from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from app.schemas.enums import GenderEnum


class IdentityBase(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100,
                                      description="First name of the individual")
    last_name: Optional[str] = Field(None, max_length=100,
                                     description="Last name of the individual")
    gender: Optional[GenderEnum] = Field(None,
                                         description="Gender of the individual")
    valid_from: Optional[date] = Field(None,
                                       description="Start date of the identity's validity")
    valid_until: Optional[date] = Field(None,
                                        description="End date of the identity's validity")

    model_config = ConfigDict(from_attributes=True)


class IdentityCreate(IdentityBase):
    individual_id: int = Field(...,
                               description="ID of the associated individual")


class IdentityUpdate(IdentityBase):
    pass


class IdentityOut(IdentityBase):
    id: int = Field(..., description="ID of the identity")
    individual_id: int = Field(...,
                               description="ID of the associated individual")

    model_config = ConfigDict(from_attributes=True)
