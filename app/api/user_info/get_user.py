from fastapi import APIRouter

from app.core.dependencies import badresponse
from app.models.auth_schemas import UserResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User


router = APIRouter()


@router.get("/get-user/{username}", response_model=UserResponse)
async def get_user(username: str):
    if not username.startswith("@"):
        username = f"@{username}"
    user = adapter.get_by_value(User, "username", username)
    if not user:
        return badresponse("User not found", 404)
    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        subscriptions_count=user.subscriptions_count,
        followers_count=user.followers_count,
        description=user.description,
        role=user.role,
    )
    return user_resp
