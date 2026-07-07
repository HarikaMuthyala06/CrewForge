# app/routers/applications.py

from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.application_schema import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStatus
)

router = APIRouter(prefix="/applications", tags=["Applications"])


def application_doc_to_response(doc: dict) -> ApplicationResponse:
    return ApplicationResponse(
        id=str(doc["_id"]),
        startup_id=str(doc["startup_id"]),
        opening_id=doc["opening_id"],
        user_id=str(doc["user_id"]),
        role_applied=doc["role_applied"],
        status=doc["status"]
    )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_to_opening(
    payload: ApplicationCreateRequest,
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

    # Find the specific opening inside the startup's openings array
    opening = next(
        (o for o in startup.get("openings", []) if o["opening_id"] == payload.opening_id),
        None
    )
    if opening is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opening not found")

    # Prevent duplicate applications — one per opening per user
    existing = await db.applications.find_one({
        "startup_id": startup_object_id,
        "opening_id": payload.opening_id,
        "user_id": current_user["_id"]
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this opening"
        )

    application_doc = {
        "startup_id": startup_object_id,
        "opening_id": payload.opening_id,
        "user_id": current_user["_id"],
        "role_applied": opening["role_name"],
        "status": ApplicationStatus.pending.value,
        "applied_at": datetime.now(timezone.utc)
    }

    result = await db.applications.insert_one(application_doc)
    application_doc["_id"] = result.inserted_id

    return application_doc_to_response(application_doc)


@router.get("/me", response_model=List[ApplicationResponse])
async def get_my_applications(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.applications.find({"user_id": current_user["_id"]})
    applications = await cursor.to_list(length=100)
    return [application_doc_to_response(a) for a in applications]


@router.get("/startup/{startup_id}", response_model=List[ApplicationResponse])
async def get_startup_applications(
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

    # Only the founder can view applications for their startup
    if startup["founder_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the founder can view applications for this startup"
        )

    cursor = db.applications.find({"startup_id": startup_object_id})
    applications = await cursor.to_list(length=100)
    return [application_doc_to_response(a) for a in applications]


@router.put("/{application_id}/accept", response_model=ApplicationResponse)
async def accept_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        app_object_id = ObjectId(application_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    application = await db.applications.find_one({"_id": app_object_id})
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # Verify the current user is the founder of the startup this application belongs to
    startup = await db.startups.find_one({"_id": application["startup_id"]})
    if startup is None or startup["founder_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the founder can accept applications"
        )

    await db.applications.update_one(
        {"_id": app_object_id},
        {"$set": {"status": ApplicationStatus.accepted.value}}
    )

    updated = await db.applications.find_one({"_id": app_object_id})
    return application_doc_to_response(updated)


@router.put("/{application_id}/reject", response_model=ApplicationResponse)
async def reject_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        app_object_id = ObjectId(application_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    application = await db.applications.find_one({"_id": app_object_id})
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    startup = await db.startups.find_one({"_id": application["startup_id"]})
    if startup is None or startup["founder_id"] != current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the founder can reject applications"
        )

    await db.applications.update_one(
        {"_id": app_object_id},
        {"$set": {"status": ApplicationStatus.rejected.value}}
    )

    updated = await db.applications.find_one({"_id": app_object_id})
    return application_doc_to_response(updated)