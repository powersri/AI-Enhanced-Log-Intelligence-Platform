from fastapi import APIRouter, Depends
from app.schemas.common import APIResponse
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.auth_service import register_user, login_user
from app.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse)
def register(payload: UserCreate):
    user = register_user(payload)
    return APIResponse(success=True, message="User registered successfully", data=user)


@router.post("/login", response_model=APIResponse)
def login(payload: UserLogin):
    token = login_user(payload)
    return APIResponse(success=True, message="Login successful", data=token)


@router.get("/me", response_model=APIResponse)
def me(current_user: dict = Depends(get_current_user)):
    return APIResponse(success=True, message="Current user fetched successfully", data=current_user)
