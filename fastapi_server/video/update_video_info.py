from fastapi import APIRouter, Depends
from dependencies import check_user, badresponse, okresp
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video, User
from models.schemas.auth_schemas import UpdateVideoContent
from typing import Annotated
from uuid import UUID

router = APIRouter()

@router.put("/update-video/{uuid}")
async def update_video(
    user: Annotated[User, Depends(check_user)],
    uuid: UUID,
    content: UpdateVideoContent):
    if not user:
        return badresponse("Unauthorized", 401)
    video = await adapter.get_by_id(Video, uuid)
    if not video:
        return badresponse("Video not found", 404)
    if video.author_id != user.id:
        return badresponse("Forbidden", 403)
    await adapter.update_by_id(Video, uuid, {"description": content.description})
    return okresp()
