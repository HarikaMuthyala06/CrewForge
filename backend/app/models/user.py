# app/models/user.py

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId


class UserModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    email: str
    password: str
    skills: List[str] = []
    role: str
    bio: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}