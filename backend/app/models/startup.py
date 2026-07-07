# app/models/startup.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List


class OpeningModel(BaseModel):
    opening_id: str
    role_name: str
    required_skills: List[str] = []
    role_description: str


class StartupModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    founder_id: str
    startup_name: str
    domain: str
    description: str
    openings: List[OpeningModel] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True