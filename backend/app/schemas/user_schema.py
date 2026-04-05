
# Import Pydantic base classes and types for data validation
from pydantic import BaseModel, EmailStr, Field



# Schema for creating a new user (registration)
class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)  # User's full name (2-100 chars)
    email: EmailStr  # User's email address (validated)
    password: str = Field(min_length=8, max_length=128)  # Password (8-128 chars)
    role: str = Field(default="viewer", min_length=3)  # User role (default: viewer)



# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr  # User's email address
    password: str  # User's password



# Public-facing schema for user data returned by the API
class UserPublic(BaseModel):
    id: str  # Unique identifier for the user
    full_name: str  # User's full name
    email: EmailStr  # User's email address
    role: str  # User's role (admin, operator, viewer)
