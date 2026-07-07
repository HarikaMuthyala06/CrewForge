# app/utils/password_utils.py

import bcrypt


def hash_password(plain_password: str) -> str:
    """
    Takes a plaintext password and returns a bcrypt hash (as a string)
    that is safe to store in MongoDB.
    """
    # bcrypt works on bytes, not Python strings, so we encode first.
    password_bytes = plain_password.encode("utf-8")

    # bcrypt has a hard limit of 72 bytes per password. Newer bcrypt
    # versions (5.0+) raise a ValueError instead of silently truncating,
    # so we check ourselves and raise a clearer, app-level error.
    if len(password_bytes) > 72:
        raise ValueError("Password must be 72 bytes or fewer.")

    # gensalt() creates a random salt. The "12" is the cost factor —
    # higher = slower = more resistant to brute-force attacks.
    salt = bcrypt.gensalt(rounds=12)

    # hashpw() does the actual hashing, combining the password and salt.
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # We stored it as bytes for hashing, but MongoDB/Pydantic prefer
    # plain strings, so we decode back to a string before returning.
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a plaintext password (typed at login) against the
    bcrypt hash stored in MongoDB (created at registration).
    Returns True if they match, False otherwise.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # checkpw() re-hashes the plain password using the SAME salt
    # that's embedded in hashed_bytes, then compares the results.
    return bcrypt.checkpw(password_bytes, hashed_bytes)