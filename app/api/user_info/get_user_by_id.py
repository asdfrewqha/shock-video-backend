from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import badresponse
from app.models.auth_schemas import UserResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User


router = APIRouter()


@router.get("/get-user-by-id/{uuid}", response_model=UserResponse)
async def get_user_by_id(uuid: UUID):
    user = await adapter.get_by_id(User, uuid)
    if not user:
        return badresponse("Not found", 404)
    user_resp = UserResponse(
        id=uuid,
        username=user.username,
        name=user.name,
        role=user.role,
    )
    return user_resp
