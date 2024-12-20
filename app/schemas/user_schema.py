from pydantic import BaseModel, Field, EmailStr, ConfigDict, \
    field_validator, model_validator
from datetime import datetime
from typing import List


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50,
                          description="Unique alphanumeric username")
    email: EmailStr = Field(...,
                            description="User's unique email address")

    model_config = ConfigDict(from_attributes=True)

    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric.')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128,
                          description="User's password")
    confirm_password: str = Field(...,
                                  description="Password confirmation")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = ConfigDict(from_attributes=True)


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    individuals: List[int] = Field(default_factory=list,
                                   description="List of individual's IDs")

    model_config = ConfigDict(from_attributes=True)
