from pydantic import BaseModel  # Import Pydantic base class for data validation


# Schema for the response returned after successful authentication (login/register)
class TokenResponse(BaseModel):
    access_token: str  # JWT access token string
    token_type: str = "bearer"  # Token type (default: bearer)


# This schema might not be used currently, but can be useful for future features