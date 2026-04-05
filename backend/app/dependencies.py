
# Import FastAPI dependencies and security utilities
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Import JWT decoding utility
from app.auth.jwt_handler import decode_access_token

# HTTPBearer instance for extracting and validating Authorization header
security = HTTPBearer()



# Dependency to get the current user from the JWT access token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    # Extract the token string from the credentials
    token = credentials.credentials
    try:
        # Decode and validate the JWT token
        payload = decode_access_token(token)
    except HTTPException:
        # Raise 401 if token is invalid or expired
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Ensure the payload contains the required subject (user ID)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    # Return user info extracted from the token payload
    return {
        "id": payload["sub"],
        "email": payload.get("email"),
        "role": payload.get("role"),
    }
