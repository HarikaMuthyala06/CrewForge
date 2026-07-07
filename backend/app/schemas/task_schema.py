# app/schemas/task_schema.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TaskStatus(str, Enum):
    todo = "Todo"
    in_progress = "In Progress"
    completed = "Completed"


class TaskCreateRequest(BaseModel):
    startup_id: str
    assigned_to: str
    title: str = Field(min_length=2, max_length=100)
    description: Optional[str] = ""


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: str
    startup_id: str
    assigned_to: str
    title: str
    description: Optional[str] = ""
    status: str