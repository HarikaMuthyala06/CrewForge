# app/schemas/startup_schema.py

from pydantic import BaseModel, Field
from typing import Optional, List


class OpeningResponse(BaseModel):
    opening_id: str
    role_name: str
    required_skills: List[str]
    role_description: str


class StartupCreateRequest(BaseModel):
    startup_name: str = Field(min_length=2, max_length=100)
    domain: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=10, max_length=2000)


class StartupUpdateRequest(BaseModel):
    startup_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    domain: Optional[str] = Field(default=None, min_length=2, max_length=50)
    description: Optional[str] = Field(default=None, min_length=10, max_length=2000)


class StartupResponse(BaseModel):
    id: str
    founder_id: str
    startup_name: str
    domain: str
    description: str
    openings: List[OpeningResponse]

class OpeningCreateRequest(BaseModel):
    role_name: str = Field(min_length=2, max_length=50)
    required_skills: List[str] = []
    role_description: str = Field(min_length=10, max_length=500)