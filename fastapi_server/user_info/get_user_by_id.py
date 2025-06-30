from uuid import UUID

from fastapi import APIRouter

from dependencies import badresponse
from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import UserResponse
from models.tables.db_tables import User


router = APIRouter()


@router.get("/get-user-by-id", response_model=UserResponse)
async def get_user_by_id(uuid: UUID):
    user = await adapter.get_by_id(User, uuid)
    if not user:
        return badresponse("Not found", 404)
    user_resp = UserResponse(
        id=uuid, username=user.username, role=user.role, avatar_url=user.avatar_url
    )
    return user_resp
