# app/schemas/user_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum


class RoleEnum(str, Enum):
    founder = "Founder"
    developer = "Developer"
    designer = "Designer"
    student = "Student"


class UserRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    skills: List[str] = []
    role: RoleEnum
    bio: Optional[str] = ""


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    skills: List[str]
    role: str
    bio: Optional[str] = ""

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    skills: Optional[List[str]] = None
    role: Optional[RoleEnum] = None
    bio: Optional[str] = None