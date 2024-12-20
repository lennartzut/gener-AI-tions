from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional
from datetime import date
from app.models.enums import GenderEnum


class IdentityBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50,
                            description="First name")
    last_name: str = Field(..., min_length=1, max_length=50,
                           description="Last name")
    gender: GenderEnum = Field(...,
                               description="Gender of the identity")
    valid_from: Optional[date] = Field(None,
                                       description="Start date of the identity's validity")
    valid_until: Optional[date] = Field(None,
                                        description="End date of the identity's validity")

    @model_validator(mode='after')
    def validate_dates(self):
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValueError(
                "Valid from date cannot be after valid until date.")
        return self

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
