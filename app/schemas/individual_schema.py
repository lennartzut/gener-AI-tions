import logging
from datetime import date
from typing import Optional, List

from pydantic import BaseModel, Field, model_validator, ConfigDict

from app.models.enums_model import GenderEnum
from app.schemas.identity_schema import IdentityOut, IdentityIdOut
from app.utils.validators import ValidationUtils

logger = logging.getLogger(__name__)


def _validate_individual_dates(birth_date: Optional[date],
                               death_date: Optional[date]) -> None:
    """
    Helper function to validate that birth_date is not after death_date.
    """
    ValidationUtils.validate_date_order([
        (birth_date, death_date,
         "Birth date must be before death date.")
    ])


class IndividualBase(BaseModel):
    """
    Base schema for an individual, including common fields.
    """
    birth_date: Optional[date] = Field(
        None,
        description="Birth date of the individual"
    )
    birth_place: Optional[str] = Field(
        None,
        max_length=100,
        description="Birthplace of the individual"
    )
    death_date: Optional[date] = Field(
        None,
        description="Death date of the individual"
    )
    death_place: Optional[str] = Field(
        None,
        max_length=100,
        description="Place of death for the individual"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the individual"
    )

    @model_validator(mode='before')
    def convert_blank_dates(cls, data):
        """
        Converts empty-string values for birth_date/death_date into None.
        """
        if not isinstance(data, dict):
            return data
        for field_name in ('birth_date', 'death_date'):
            if field_name in data and isinstance(data[field_name],
                                                 str):
                if not data[field_name].strip():
                    data[field_name] = None
        return data

    @model_validator(mode='after')
    def validate_dates(cls,
                       values: "IndividualBase") -> "IndividualBase":
        """
        Validates that birth_date is not after death_date.
        """
        try:
            _validate_individual_dates(values.birth_date,
                                       values.death_date)
        except ValueError as ve:
            logger.error(f"Validation failed: {ve}")
            raise ValueError(str(ve)) from ve
        return values

    model_config = ConfigDict(from_attributes=False)


class IndividualCreate(IndividualBase):
    """
    Schema for creating a new individual.
    """
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="First name of the individual"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Last name of the individual"
    )
    gender: GenderEnum = Field(
        ...,
        description="Gender of the individual"
    )


class IndividualUpdate(IndividualBase):
    """
    Schema for updating an existing individual.
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


class IndividualOut(BaseModel):
    """
    Schema for returning individual data.
    """
    id: int = Field(
        ...,
        description="The unique ID of the individual"
    )
    individual_number: int = Field(
        ...,
        description="A unique number assigned to the individual"
    )
    birth_date: Optional[date] = Field(
        None,
        description="Birth date of the individual"
    )
    birth_place: Optional[str] = Field(
        None,
        description="Birthplace of the individual"
    )
    death_date: Optional[date] = Field(
        None,
        description="Death date of the individual"
    )
    death_place: Optional[str] = Field(
        None,
        description="Place of death for the individual"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the individual"
    )
    age: Optional[int] = Field(
        None,
        description="Age of the individual, calculated if applicable"
    )
    primary_identity: Optional[IdentityOut] = Field(
        None,
        description="Details of the primary identity associated with the individual"
    )
    identities: List[IdentityIdOut] = Field(
        default_factory=list,
        description="List of minimal identity objects containing only the ID"
    )

    @model_validator(mode='after')
    def populate_age(cls,
                     values: "IndividualOut") -> "IndividualOut":
        """
        Calculates and populates the age based on birth and death dates if not already set.
        """
        if not values.age and values.birth_date:
            values.age = ValidationUtils.calculate_age(
                values.birth_date, values.death_date)
        return values

    model_config = ConfigDict(from_attributes=True)
