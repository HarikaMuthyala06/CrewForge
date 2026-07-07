# app/routers/auth.py

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from app.database import get_db
from app.schemas.user_schema import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.utils.password_utils import hash_password, verify_password
from app.utils.jwt_utils import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest):
    db = get_db()

    # Check if a user with this email already exists.
    existing_user = await db.users.find_one({"email": payload.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the plaintext password before storing anything.
    try:
        hashed_pw = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Build the document to insert into MongoDB.
    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password": hashed_pw,
        "skills": payload.skills,
        "role": payload.role.value,
        "bio": payload.bio,
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.users.insert_one(user_doc)
    new_user_id = str(result.inserted_id)

    # Create a JWT for this brand-new user, so they're logged in immediately.
    token = create_access_token({"sub": new_user_id})

    user_response = UserResponse(
        id=new_user_id,
        name=user_doc["name"],
        email=user_doc["email"],
        skills=user_doc["skills"],
        role=user_doc["role"],
        bio=user_doc["bio"]
    )

    return TokenResponse(access_token=token, user=user_response)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest):
    db = get_db()

    user = await db.users.find_one({"email": payload.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(user["_id"])})

    user_response = UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        skills=user.get("skills", []),
        role=user["role"],
        bio=user.get("bio", "")
    )

    return TokenResponse(access_token=token, user=user_response)