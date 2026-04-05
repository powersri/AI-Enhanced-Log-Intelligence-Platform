
# Import FastAPI exception and status codes for error handling
from fastapi import HTTPException, status
# Import database connection utility
from app.db.mongo import get_db
# Import valid user roles
from app.models.user_model import USER_ROLES
# Import user schema classes
from app.schemas.user_schema import UserCreate, UserLogin
# Import password hashing and verification utilities
from app.auth.password import hash_password, verify_password
# Import JWT token creation utility
from app.auth.jwt_handler import create_access_token



# Register a new user in the database
def register_user(payload: UserCreate):
    db = get_db()  # Get MongoDB database connection
    role = payload.role.lower()  # Normalize role to lowercase

    # Validate the user role
    if role not in USER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check if the email is already registered
    existing_user = db.users.find_one({"email": payload.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Prepare the user document for insertion
    doc = {
        "full_name": payload.full_name,
        "email": payload.email.lower(),
        "password": hash_password(payload.password),  # Store hashed password
        "role": role,
    }
    result = db.users.insert_one(doc)  # Insert user into the database

    # Return the public user info
    return {
        "id": str(result.inserted_id),
        "full_name": payload.full_name,
        "email": payload.email.lower(),
        "role": role,
    }



# Authenticate a user and return a JWT access token
def login_user(payload: UserLogin):
    db = get_db()  # Get MongoDB database connection
    # Find the user by email
    user = db.users.find_one({"email": payload.email.lower()})

    # Check if user exists and password is correct
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create a JWT access token with user info
    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
    })

    # Return the token and its type
    return {"access_token": token, "token_type": "bearer"}
