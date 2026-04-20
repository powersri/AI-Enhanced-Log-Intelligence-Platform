from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.common import APIResponse
from app.schemas.user_schema import UserCreate, UserLogin
from app.services.auth_service import login_user, register_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse)
def register(payload: UserCreate):
    user = register_user(payload)
    return APIResponse(
        success=True,
        message="User registered successfully",
        data=user,
    )


@router.post("/login", response_model=APIResponse)
def login(payload: UserLogin):
    token = login_user(payload)
    return APIResponse(
        success=True,
        message="Login successful",
        data={
            "access_token": token["access_token"],
            "token_type": token["token_type"],
        },
    )


@router.get("/me", response_model=APIResponse)
def me(current_user: dict = Depends(get_current_user)):
    return APIResponse(
        success=True,
        message="Current user fetched successfully",
        data=current_user,
    )