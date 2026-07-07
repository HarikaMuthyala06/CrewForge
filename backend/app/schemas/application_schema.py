# app/schemas/application_schema.py

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ApplicationStatus(str, Enum):
    pending = "Pending"
    accepted = "Accepted"
    rejected = "Rejected"


class ApplicationCreateRequest(BaseModel):
    startup_id: str
    opening_id: str


class ApplicationResponse(BaseModel):
    id: str
    startup_id: str
    opening_id: str
    user_id: str
    role_applied: str
    status: str