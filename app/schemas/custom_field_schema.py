from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List


class CustomFieldBase(BaseModel):
    table_name: str = Field(...,
                            description="Target table name (e.g., 'individuals')")
    field_name: str = Field(...,
                            description="Name of the custom field")
    field_type: str = Field(...,
                            description="Data type of the field (e.g., 'string', 'date')")

    model_config = ConfigDict(from_attributes=True)


class CustomFieldCreate(CustomFieldBase):
    user_id: int = Field(...,
                         description="ID of the user who created this field")


class CustomFieldUpdate(CustomFieldBase):
    pass


class CustomFieldOut(CustomFieldBase):
    id: int
    created_at: datetime

    # We'll assume values are listed separately if needed
    # Just show field metadata here

    model_config = ConfigDict(from_attributes=True)
