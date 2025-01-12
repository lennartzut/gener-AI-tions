import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, \
    field_validator, model_validator


class UserBase(BaseModel):
    """
    Base schema for a user, including common fields.
    """
    username: str = Field(..., min_length=3, max_length=50,
                          description="The username of the user")
    email: EmailStr = Field(...,
                            description="The email address of the user")

    model_config = ConfigDict(from_attributes=True)

    @field_validator('username')
    def username_pattern(cls, v: str) -> str:
        """
        Validates the username to ensure it starts with a letter and contains
        only letters, digits, underscores, or dots.
        """
        pattern = r'^[A-Za-z][A-Za-z0-9_.]*$'
        if not re.match(pattern, v):
            raise ValueError(
                'Username must start with a letter and contain only letters, digits, underscores, or dots.')
        return v


class UserCreate(UserBase):
    """
    Schema for creating a new user, including password fields.
    """
    password: str = Field(..., min_length=8, max_length=128,
                          description="The password for the user")
    confirm_password: str = Field(...,
                                  description="The password confirmation")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def check_passwords_match(self):
        """
        Ensures that the password and confirm_password fields match.
        """
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    """
    email: EmailStr = Field(...,
                            description="The email address of the user")
    password: str = Field(..., min_length=8, max_length=128,
                          description="The password for the user")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Schema for updating user details.
    """
    username: Optional[str] = Field(None, min_length=3,
                                    max_length=50,
                                    description="The updated username of the user")
    email: Optional[EmailStr] = Field(None,
                                      description="The updated email address of the user")
    password: Optional[str] = Field(None, min_length=8,
                                    max_length=128,
                                    description="The updated password")
    confirm_password: Optional[str] = Field(None,
                                            description="The updated password confirmation")

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def check_passwords_match(self):
        """
        Ensures that the password and confirm_password fields match, if both are provided.
        """
        if self.password or self.confirm_password:
            if self.password != self.confirm_password:
                raise ValueError("Passwords do not match.")
        return self


class UserOut(UserBase):
    """
    Schema for returning user data, including related entity IDs and admin status.
    """
    id: int = Field(..., description="The unique ID of the user")
    is_admin: bool = Field(...,
                           description="Indicates if the user has admin privileges")
    created_at: datetime = Field(...,
                                 description="The timestamp when the user was created")
    updated_at: datetime = Field(...,
                                 description="The timestamp when the user was last updated")

    model_config = ConfigDict(from_attributes=True)
