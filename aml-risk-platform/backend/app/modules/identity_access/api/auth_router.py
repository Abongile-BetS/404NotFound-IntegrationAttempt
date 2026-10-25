from fastapi import APIRouter, Depends

from app.modules.identity_access.application.auth_service import AuthService
from app.modules.identity_access.schemas.user_response import UserResponse
from app.shared.auth.dependencies import get_current_user, require_role


router = APIRouter(tags=["Identity Access"])
service = AuthService()


@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return service.to_user_response(current_user)


@router.get("/admin-test")
async def admin_test(current_user: dict = Depends(require_role("admin"))):
    return {
        "message": "You have admin access",
        "username": current_user.get("preferred_username"),
    }
