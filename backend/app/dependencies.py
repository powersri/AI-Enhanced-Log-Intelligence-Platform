# Import FastAPI dependencies and security utilities
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Import database and JWT utility
from app.db.mongo import db, parse_object_id
from app.auth.jwt_handler import decode_access_token

# HTTPBearer instance for extracting and validating Authorization header
security = HTTPBearer()


# Dependency to get the current authenticated user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id = payload["sub"]

    # Verify user still exists in the database
    user = db.users.find_one({"_id": parse_object_id(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
    }