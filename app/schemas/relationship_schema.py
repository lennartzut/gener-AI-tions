from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import FamilyRelationshipEnum
from app.schemas.individual_schema import IndividualOut


class RelationshipBase(BaseModel):
    individual_id: int = Field(...,
                               description="ID of the 'primary' individual in the relationship")
    related_id: int = Field(...,
                            description="ID of the 'related' individual in the relationship")
    relationship_type: FamilyRelationshipEnum = Field(...,
                                                      description="Type of relationship")

    model_config = ConfigDict(from_attributes=True)


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipUpdate(RelationshipBase):
    pass


class RelationshipOut(RelationshipBase):
    id: int = Field(..., description="ID of the relationship")
    individual: IndividualOut = Field(...,
                                      description="The 'primary' individual")
    related: IndividualOut = Field(...,
                                   description="The 'related' individual")

    model_config = ConfigDict(from_attributes=True)
