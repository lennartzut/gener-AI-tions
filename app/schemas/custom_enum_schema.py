from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CustomEnumBase(BaseModel):
    enum_name: str = Field(...,
                           description="Name of the enum (e.g., 'gender')")
    enum_value: str = Field(...,
                            description="Value added (e.g., 'non-binary')")

    model_config = ConfigDict(from_attributes=True)


class CustomEnumCreate(CustomEnumBase):
    user_id: int = Field(...,
                         description="ID of the user who added this enum")


class CustomEnumUpdate(CustomEnumBase):
    pass


class CustomEnumOut(CustomEnumBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
