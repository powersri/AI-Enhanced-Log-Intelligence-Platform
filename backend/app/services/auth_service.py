from fastapi import HTTPException, status

from app.auth.jwt_handler import create_access_token
from app.auth.password import hash_password, verify_password
from app.db.mongo import db
from app.models.user_model import USER_ROLES
from app.schemas.user_schema import UserCreate, UserLogin


def register_user(payload: UserCreate):
    role = payload.role.lower()
    email = payload.email.lower()

    if role not in USER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_user = db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "full_name": payload.full_name,
        "email": email,
        "password": hash_password(payload.password),
        "role": role,
    }
    result = db.users.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "full_name": payload.full_name,
        "email": email,
        "role": role,
    }


def login_user(payload: UserLogin):
    email = payload.email.lower()
    user = db.users.find_one({"email": email})

    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        {
            "sub": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
        }
    )

    return {"access_token": token, "token_type": "bearer"}