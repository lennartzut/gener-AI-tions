from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# User Registration Schema
class UserCreate(BaseModel):
    email: EmailStr = Field(...,
                            description="User's unique email address")
    password: str = Field(..., min_length=8,
                          description="User's password")


# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


# User Output Schema
class UserOut(BaseModel):
    id: int
    email: EmailStr
    avatar: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
