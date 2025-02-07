from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator, ConfigDict

from app.models.enums_model import (
    InitialRelationshipEnum,
    HorizontalRelationshipTypeEnum,
    VerticalRelationshipTypeEnum
)
from app.schemas.individual_schema import IndividualOut
from app.utils.validators import ValidationUtils


# Helper function to validate relationship dates
def _validate_relationship_dates(union_date: Optional[date],
                                 dissolution_date: Optional[
                                     date]) -> None:
    ValidationUtils.validate_date_order([
        (union_date, dissolution_date,
         "Union date must be before dissolution date.")
    ])


# Helper function to validate relationship_detail based on initial_relationship.
def _validate_relationship_detail(
        initial_relationship: InitialRelationshipEnum,
        detail: Optional[str]) -> None:
    if detail is None:
        return
    if initial_relationship == InitialRelationshipEnum.PARTNER:
        # For partners, we expect a detail from the HorizontalRelationshipTypeEnum.
        valid_values = [e.value for e in
                        HorizontalRelationshipTypeEnum]
        if detail not in valid_values:
            raise ValueError(
                "Invalid `relationship_detail` for partners.")
    elif initial_relationship in {InitialRelationshipEnum.CHILD,
                                  InitialRelationshipEnum.PARENT}:
        # For child/parent, we expect a detail from the VerticalRelationshipTypeEnum.
        valid_values = [e.value for e in
                        VerticalRelationshipTypeEnum]
        if detail not in valid_values:
            raise ValueError(
                "Invalid `relationship_detail` for child/parent.")


class RelationshipBase(BaseModel):
    """
    Base schema for a relationship, including validation logic.
    """
    individual_id: int = Field(
        ...,
        description="The ID of the primary individual in the relationship"
    )
    related_id: int = Field(
        ...,
        description="The ID of the related individual in the relationship"
    )
    initial_relationship: InitialRelationshipEnum = Field(
        ...,
        description="The initial type of relationship (e.g., child, parent, partner)"
    )
    relationship_detail: Optional[str] = Field(
        None,
        description="Further detail about the relationship"
    )
    union_date: Optional[date] = Field(
        None,
        description="The union date for partner relationships"
    )
    union_place: Optional[str] = Field(
        None,
        description="The union place for partner relationships"
    )
    dissolution_date: Optional[date] = Field(
        None,
        description="The dissolution date for the relationship"
    )
    notes: Optional[str] = Field(
        None,
        max_length=255,
        description="Additional notes about the relationship"
    )

    @model_validator(mode='before')
    def convert_blank_dates(cls, data):
        """
        Converts empty-string values for union_date/dissolution_date into None.
        """
        if not isinstance(data, dict):
            return data
        for field_name in ('union_date', 'dissolution_date'):
            if field_name in data and isinstance(data[field_name],
                                                 str):
                if not data[field_name].strip():
                    data[field_name] = None
        return data

    @model_validator(mode='after')
    def validate_relationship_detail(cls,
                                     values: "RelationshipBase") -> "RelationshipBase":
        """
        Validates that `relationship_detail` is valid based on `initial_relationship`.
        """
        _validate_relationship_detail(values.initial_relationship,
                                      values.relationship_detail)
        return values

    @model_validator(mode='after')
    def validate_dates(cls,
                       values: "RelationshipBase") -> "RelationshipBase":
        """
        Validates that union_date is not after dissolution_date.
        """
        _validate_relationship_dates(values.union_date,
                                     values.dissolution_date)
        return values

    model_config = ConfigDict(from_attributes=True)


class RelationshipCreate(RelationshipBase):
    """
    Schema for creating a new relationship.
    """
    pass


class RelationshipUpdate(BaseModel):
    """
    Schema for updating an existing relationship.
    """
    initial_relationship: Optional[InitialRelationshipEnum] = Field(
        None,
        description="Updated initial type of relationship"
    )
    relationship_detail: Optional[str] = Field(
        None,
        description="Updated relationship detail"
    )
    union_date: Optional[date] = Field(
        None,
        description="Updated union date for partner relationships"
    )
    union_place: Optional[str] = Field(
        None,
        description="Updated union place for partner relationships"
    )
    dissolution_date: Optional[date] = Field(
        None,
        description="Updated dissolution date for the relationship"
    )
    notes: Optional[str] = Field(
        None,
        max_length=255,
        description="Updated additional notes about the relationship"
    )
    individual_id: Optional[int] = Field(
        None,
        description="Updated primary individual ID in the relationship"
    )
    related_id: Optional[int] = Field(
        None,
        description="Updated related individual ID in the relationship"
    )

    @model_validator(mode='after')
    def validate_relationship_detail(cls,
                                     values: "RelationshipUpdate") -> "RelationshipUpdate":
        """
        Validates that `relationship_detail` is valid based on `initial_relationship`, if provided.
        """
        if values.relationship_detail is not None and values.initial_relationship is not None:
            _validate_relationship_detail(
                values.initial_relationship,
                values.relationship_detail)
        return values

    @model_validator(mode='after')
    def validate_dates(cls,
                       values: "RelationshipUpdate") -> "RelationshipUpdate":
        """
        Validates that union_date is not after dissolution_date.
        """
        _validate_relationship_dates(values.union_date,
                                     values.dissolution_date)
        return values

    model_config = ConfigDict(from_attributes=True)


class RelationshipOut(RelationshipBase):
    """
    Schema for returning relationship data.
    """
    id: int = Field(
        ...,
        description="The unique ID of the relationship"
    )
    created_at: datetime = Field(
        ...,
        description="The timestamp when the relationship was created"
    )
    updated_at: datetime = Field(
        ...,
        description="The timestamp when the relationship was last updated"
    )
    individual: IndividualOut = Field(
        ...,
        description="Details of the primary individual in the relationship"
    )
    related: IndividualOut = Field(
        ...,
        description="Details of the related individual in the relationship"
    )

    model_config = ConfigDict(from_attributes=True)
