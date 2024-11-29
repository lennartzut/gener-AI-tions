from pydantic import BaseModel, Field, EmailStr, ConfigDict, \
    field_validator
from datetime import datetime


# User Registration Schema
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's unique email address")
    password: str = Field(..., min_length=8, description="User's password")

    @field_validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric.'
        return v

    model_config = ConfigDict(from_attributes=True)


# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = ConfigDict(from_attributes=True)


# User Output Schema
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
