from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator, ConfigDict

from app.models.enums_model import InitialRelationshipEnum, \
    HorizontalRelationshipTypeEnum, VerticalRelationshipTypeEnum
from app.schemas.individual_schema import IndividualOut
from app.utils.validators_utils import ValidationUtils


class RelationshipBase(BaseModel):
    """
    Base schema for a relationship, including validation logic.
    """
    individual_id: int = Field(...,
                               description="The ID of the primary individual in the relationship")
    related_id: int = Field(...,
                            description="The ID of the related individual in the relationship")
    initial_relationship: InitialRelationshipEnum = Field(...,
                                                          description="The initial type of relationship (e.g., child, parent, partner)")
    relationship_detail: Optional[str] = Field(None,
                                               description="Further detail about the relationship")
    union_date: Optional[date] = Field(None,
                                       description="The union date for partner relationships")
    union_place: Optional[str] = Field(None,
                                       description="The union place for partner relationships")
    dissolution_date: Optional[date] = Field(None,
                                             description="The dissolution date for the relationship")
    notes: Optional[str] = Field(None, max_length=255,
                                 description="Additional notes about the relationship")

    @model_validator(mode='after')
    def validate_relationship_detail(cls,
                                     values: 'RelationshipBase') -> 'RelationshipBase':
        """
        Validates that `relationship_detail` corresponds to the correct enum based on `initial_relationship`.
        """
        if values.relationship_detail is None:
            return values
        if values.initial_relationship == InitialRelationshipEnum.PARTNER:
            if values.relationship_detail not in [e.value for e in
                                                  VerticalRelationshipTypeEnum]:
                raise ValueError(
                    "Invalid `relationship_detail` for partners.")
        elif values.initial_relationship in {
            InitialRelationshipEnum.CHILD,
            InitialRelationshipEnum.PARENT}:
            if values.relationship_detail not in [e.value for e in
                                                  HorizontalRelationshipTypeEnum]:
                raise ValueError(
                    "Invalid `relationship_detail` for child/parent.")
        return values

    @model_validator(mode='after')
    def validate_dates(cls,
                       values: "RelationshipBase") -> "RelationshipBase":
        ValidationUtils.validate_date_order([
            (values.union_date, values.dissolution_date,
             "Union date must be before dissolution date.")
        ])
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
        None, description="Updated initial type of relationship")
    relationship_detail: Optional[str] = Field(None,
                                               description="Updated relationship detail")
    union_date: Optional[date] = Field(None,
                                       description="Updated union date for partner relationships")
    union_place: Optional[str] = Field(None,
                                       description="Updated union place for partner relationships")
    dissolution_date: Optional[date] = Field(None,
                                             description="Updated dissolution date for the relationship")
    notes: Optional[str] = Field(None, max_length=255,
                                 description="Updated additional notes about the relationship")
    individual_id: Optional[int] = Field(None,
                                         description="Updated primary individual ID in the relationship")
    related_id: Optional[int] = Field(None,
                                      description="Updated related individual ID in the relationship")

    @model_validator(mode='after')
    def validate_dates(cls,
                       values: "RelationshipBase") -> "RelationshipBase":
        ValidationUtils.validate_date_order([
            (values.union_date, values.dissolution_date,
             "Union date must be before dissolution date.")
        ])
        return values

    model_config = ConfigDict(from_attributes=True)


class RelationshipOut(RelationshipBase):
    """
    Schema for returning relationship data.
    """
    id: int = Field(...,
                    description="The unique ID of the relationship")
    created_at: datetime = Field(...,
                                 description="The timestamp when the relationship was created")
    updated_at: datetime = Field(...,
                                 description="The timestamp when the relationship was last updated")
    individual: IndividualOut = Field(...,
                                      description="Details of the primary individual in the relationship")
    related: IndividualOut = Field(...,
                                   description="Details of the related individual in the relationship")

    model_config = ConfigDict(from_attributes=True)