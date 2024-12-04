from pydantic import BaseModel, Field, ConfigDict, constr, \
    model_validator
from typing import Optional
from datetime import date
from app.models.enums import GenderEnum


class IdentityBase(BaseModel):
    first_name: Optional[
        constr(min_length=1, max_length=100)] = Field(None,
                                                      description="First name of the individual")
    last_name: Optional[
        constr(min_length=1, max_length=100)] = Field(None,
                                                      description="Last name of the individual")
    gender: Optional[GenderEnum] = Field(None,
                                         description="Gender of the individual")
    valid_from: Optional[date] = Field(None,
                                       description="Start date of the identity's validity")
    valid_until: Optional[date] = Field(None,
                                        description="End date of the identity's validity")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    def check_date_range(cls, values):
        valid_from = values.get('valid_from')
        valid_until = values.get('valid_until')
        if valid_from and valid_until and valid_until < valid_from:
            raise ValueError(
                "valid_until cannot be earlier than valid_from")
        return values


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
