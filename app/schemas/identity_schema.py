import logging
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator, ConfigDict

from app.models.enums_model import GenderEnum
from app.utils.validators import ValidationUtils

logger = logging.getLogger(__name__)


def _validate_identity_dates(valid_from: Optional[date],
                             valid_until: Optional[date]) -> None:
    """
    Helper function to validate that valid_from is not after valid_until.
    """
    ValidationUtils.validate_date_order([
        (valid_from, valid_until,
         "Valid from date cannot be after valid until date.")
    ])


class IdentityBase(BaseModel):
    """
    Base schema for an identity, including common fields.
    """
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="First name of the individual"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Last name of the individual"
    )
    gender: Optional[GenderEnum] = Field(
        None,
        description="Gender of the individual"
    )
    valid_from: Optional[date] = Field(
        None,
        description="The start date of this identity's validity"
    )
    valid_until: Optional[date] = Field(
        None,
        description="The end date of this identity's validity"
    )

    @model_validator(mode='before')
    def convert_blank_dates(cls, data):
        """
        Converts empty-string values for valid_from/valid_until into None.
        """
        if not isinstance(data, dict):
            return data
        for field_name in ('valid_from', 'valid_until'):
            if field_name in data and isinstance(data[field_name],
                                                 str):
                if not data[field_name].strip():
                    data[field_name] = None
        return data

    @model_validator(mode='after')
    def validate_dates(cls,
                       values: "IdentityBase") -> "IdentityBase":
        """
        Validates that valid_from is not after valid_until.
        """
        _validate_identity_dates(values.valid_from,
                                 values.valid_until)
        return values

    model_config = ConfigDict(from_attributes=True)


class IdentityCreate(IdentityBase):
    """
    Schema for creating a new identity.
    """
    individual_id: int = Field(
        ...,
        description="ID of the associated individual"
    )


class IdentityUpdate(BaseModel):
    """
    Schema for updating an existing identity.
    """
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Updated first name"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Updated last name"
    )
    gender: Optional[GenderEnum] = Field(
        None,
        description="Updated gender"
    )
    valid_from: Optional[date] = Field(
        None,
        description="Updated start date of validity"
    )
    valid_until: Optional[date] = Field(
        None,
        description="Updated end date of validity"
    )
    is_primary: Optional[bool] = Field(
        None,
        description="Whether this identity is the primary identity"
    )

    @model_validator(mode='after')
    def validate_dates(cls,
                       values: "IdentityUpdate") -> "IdentityUpdate":
        """
        Validates that valid_from is not after valid_until.
        """
        try:
            _validate_identity_dates(values.valid_from,
                                     values.valid_until)
        except ValueError as ve:
            logger.error(f"Validation failed: {ve}")
            raise ValueError(str(ve)) from ve
        return values

    model_config = ConfigDict(from_attributes=True)


class IdentityOut(IdentityBase):
    """
    Schema for returning identity data.
    """
    id: int = Field(
        ...,
        description="The unique ID of the identity"
    )
    individual_id: int = Field(
        ...,
        description="The ID of the associated individual"
    )
    identity_number: int = Field(
        ...,
        description="A unique number assigned to the identity"
    )
    is_primary: bool = Field(
        ...,
        description="Indicates if this is the primary identity"
    )
    created_at: datetime = Field(
        ...,
        description="The timestamp when this identity was created"
    )
    updated_at: datetime = Field(
        ...,
        description="The timestamp when this identity was last updated"
    )

    model_config = ConfigDict(from_attributes=True)


class IdentityIdOut(BaseModel):
    """
    Minimal schema that only includes the 'id' field from an Identity.
    """
    id: int = Field(
        ...,
        description="The unique ID of the identity"
    )

    model_config = ConfigDict(from_attributes=True)
