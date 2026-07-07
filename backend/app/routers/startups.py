# app/routers/startups.py
from app.schemas.startup_schema import OpeningCreateRequest
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.startup_schema import (
    StartupCreateRequest,
    StartupUpdateRequest,
    StartupResponse
)

router = APIRouter(prefix="/startups", tags=["Startups"])


def startup_doc_to_response(doc: dict) -> StartupResponse:
    """Converts a raw MongoDB startup document into a safe response object."""
    return StartupResponse(
        id=str(doc["_id"]),
        founder_id=str(doc["founder_id"]),
        startup_name=doc["startup_name"],
        domain=doc["domain"],
        description=doc["description"],
        openings=doc.get("openings", [])
    )


@router.post("", response_model=StartupResponse, status_code=status.HTTP_201_CREATED)
async def create_startup(
    payload: StartupCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    startup_doc = {
        "founder_id": current_user["_id"],
        "startup_name": payload.startup_name,
        "domain": payload.domain,
        "description": payload.description,
        "openings": [],
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.startups.insert_one(startup_doc)
    startup_doc["_id"] = result.inserted_id

    return startup_doc_to_response(startup_doc)


@router.get("", response_model=List[StartupResponse])
async def list_startups():
    db = get_db()
    startups_cursor = db.startups.find()
    startups = await startups_cursor.to_list(length=100)
    return [startup_doc_to_response(s) for s in startups]


@router.get("/{startup_id}", response_model=StartupResponse)
async def get_startup(startup_id: str):
    db = get_db()

    try:
        object_id = ObjectId(startup_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    startup = await db.startups.find_one({"_id": object_id})
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    return startup_doc_to_response(startup)


@router.put("/{startup_id}", response_model=StartupResponse)
async def update_startup(
    startup_id: str,
    payload: StartupUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        object_id = ObjectId(startup_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    startup = await db.startups.find_one({"_id": object_id})
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    # THE FOUNDER-ONLY CHECK — Section 7 of the SRS, implemented for real.
    if startup["founder_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the founder of this startup can update it"
        )

    update_data = payload.model_dump(exclude_unset=True)

    if update_data:
        await db.startups.update_one({"_id": object_id}, {"$set": update_data})

    updated_startup = await db.startups.find_one({"_id": object_id})
    return startup_doc_to_response(updated_startup)
@router.post("/{startup_id}/openings", response_model=StartupResponse, status_code=status.HTTP_201_CREATED)
async def add_opening(
    startup_id: str,
    payload: OpeningCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        object_id = ObjectId(startup_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    startup = await db.startups.find_one({"_id": object_id})
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    if startup["founder_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the founder of this startup can add openings"
        )

    new_opening = {
        "opening_id": str(uuid.uuid4()),
        "role_name": payload.role_name,
        "required_skills": payload.required_skills,
        "role_description": payload.role_description
    }

    await db.startups.update_one(
        {"_id": object_id},
        {"$push": {"openings": new_opening}}
    )

    updated_startup = await db.startups.find_one({"_id": object_id})
    return startup_doc_to_response(updated_startup)

@router.delete("/{startup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_startup(
    startup_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        object_id = ObjectId(startup_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    startup = await db.startups.find_one({"_id": object_id})
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found")

    if startup["founder_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the founder of this startup can delete it"
        )

    await db.startups.delete_one({"_id": object_id})
    return None