# app/routers/tasks.py

from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.task_schema import (
    TaskCreateRequest,
    TaskStatusUpdateRequest,
    TaskResponse,
    TaskStatus
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def task_doc_to_response(doc: dict) -> TaskResponse:
    return TaskResponse(
        id=str(doc["_id"]),
        startup_id=str(doc["startup_id"]),
        assigned_to=str(doc["assigned_to"]),
        title=doc["title"],
        description=doc.get("description", ""),
        status=doc["status"]
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    # Validate startup exists
    try:
        startup_object_id = ObjectId(payload.startup_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    startup = await db.startups.find_one({"_id": startup_object_id})
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    # Only the founder can create tasks
    if startup["founder_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the founder can create tasks"
        )

    # Validate assigned_to user exists
    try:
        assignee_object_id = ObjectId(payload.assigned_to)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee user not found")

    assignee = await db.users.find_one({"_id": assignee_object_id})
    if assignee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee user not found")

    task_doc = {
        "startup_id": startup_object_id,
        "assigned_to": assignee_object_id,
        "title": payload.title,
        "description": payload.description,
        "status": TaskStatus.todo.value,
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.tasks.insert_one(task_doc)
    task_doc["_id"] = result.inserted_id

    return task_doc_to_response(task_doc)


@router.get("/startup/{startup_id}", response_model=List[TaskResponse])
async def get_startup_tasks(
    startup_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        startup_object_id = ObjectId(startup_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    startup = await db.startups.find_one({"_id": startup_object_id})
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    cursor = db.tasks.find({"startup_id": startup_object_id})
    tasks = await cursor.to_list(length=100)
    return [task_doc_to_response(t) for t in tasks]


@router.get("/me", response_model=List[TaskResponse])
async def get_my_tasks(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.tasks.find({"assigned_to": current_user["_id"]})
    tasks = await cursor.to_list(length=100)
    return [task_doc_to_response(t) for t in tasks]


@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: str,
    payload: TaskStatusUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        task_object_id = ObjectId(task_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task = await db.tasks.find_one({"_id": task_object_id})
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Only the assigned team member can update their own task status
    if task["assigned_to"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned team member can update this task"
        )

    await db.tasks.update_one(
        {"_id": task_object_id},
        {"$set": {"status": payload.status.value}}
    )

    updated_task = await db.tasks.find_one({"_id": task_object_id})
    return task_doc_to_response(updated_task)