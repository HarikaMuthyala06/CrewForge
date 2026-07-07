# app/core/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from bson.errors import InvalidId

from app.database import get_db
from app.utils.jwt_utils import decode_access_token

# HTTPBearer expects "Authorization: Bearer <token>" and gives us just
# the token string — no OAuth2 username/password flow involved.
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    """
    Runs on every protected route. Verifies the JWT, looks up the
    matching user in MongoDB, and returns that user's document.
    Raises 401 if anything is wrong.
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        raise credentials_exception

    db = get_db()
    user = await db.users.find_one({"_id": object_id})
    if user is None:
        raise credentials_exception

    return user