# app/utils/jwt_utils.py

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import settings


def create_access_token(data: dict) -> str:
    """
    Creates a signed JWT containing the given data (usually the user's id),
    plus an expiry time. This is what we hand back to the frontend after
    a successful login.
    """
    # Copy the input dict so we don't accidentally mutate the caller's data.
    to_encode = data.copy()

    # Calculate when this token should stop being valid.
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    # "exp" is a reserved claim name in the JWT spec — jose understands
    # it automatically and will reject the token once this time passes.
    to_encode.update({"exp": expire})

    # Encode + sign the token using our secret key and chosen algorithm.
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Verifies a JWT's signature and expiry, then returns its payload (the
    data we originally put in) if valid. Returns None if the token is
    invalid, tampered with, or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None