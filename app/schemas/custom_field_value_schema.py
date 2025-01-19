from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CustomFieldValueBase(BaseModel):
    record_id: int = Field(...,
                           description="ID of the related record in target table")
    value: Optional[str] = Field(None,
                                 description="Value of the custom field")

    model_config = ConfigDict(from_attributes=True)


class CustomFieldValueCreate(CustomFieldValueBase):
    custom_field_id: int = Field(...,
                                 description="ID of the custom field definition")


class CustomFieldValueUpdate(CustomFieldValueBase):
    pass


class CustomFieldValueOut(CustomFieldValueBase):
    id: int
    custom_field_id: int

    model_config = ConfigDict(from_attributes=True)
