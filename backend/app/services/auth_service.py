from bson import ObjectId
from fastapi import HTTPException, status
from app.db.mongo import get_db
from app.models.user_model import USER_ROLES
from app.schemas.user_schema import UserCreate, UserLogin
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token


def register_user(payload: UserCreate):
    db = get_db()

    if payload.role not in USER_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing_user = db.users.find_one({"email": payload.email.lower()})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "full_name": payload.full_name,
        "email": payload.email.lower(),
        "password": hash_password(payload.password),
        "role": payload.role,
    }
    result = db.users.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "full_name": payload.full_name,
        "email": payload.email.lower(),
        "role": payload.role,
    }


def login_user(payload: UserLogin):
    db = get_db()
    user = db.users.find_one({"email": payload.email.lower()})

    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
    })

    return {"access_token": token, "token_type": "bearer"}
