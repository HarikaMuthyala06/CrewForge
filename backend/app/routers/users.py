# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.user_schema import UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        skills=current_user.get("skills", []),
        role=current_user["role"],
        bio=current_user.get("bio", "")
    )


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    update_data = payload.model_dump(exclude_unset=True)

    if update_data.get("role") is not None:
        update_data["role"] = update_data["role"].value

    if update_data:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_data}
        )

    updated_user = await db.users.find_one({"_id": current_user["_id"]})

    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        skills=updated_user.get("skills", []),
        role=updated_user["role"],
        bio=updated_user.get("bio", "")
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user = await db.users.find_one({"_id": object_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        skills=user.get("skills", []),
        role=user["role"],
        bio=user.get("bio", "")
    )