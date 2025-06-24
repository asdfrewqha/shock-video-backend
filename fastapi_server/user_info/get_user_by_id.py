from uuid import UUID

from fastapi import APIRouter

from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import UserResponse
from models.tables.db_tables import User

router = APIRouter()


@router.get("/get-user-by-id")
async def get_user_by_id(uuid: UUID):
    user = adapter.get_by_id(User, uuid)
    user_resp = UserResponse(
        id=uuid,
        username=user.username,
        role=user.role,
        avatar_url=user.avatar_url)
    return user_resp
