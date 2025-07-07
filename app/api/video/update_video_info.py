from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user, okresp
from app.models.auth_schemas import UpdateVideoContent
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User, Video


router = APIRouter()


@router.put("/update-video/{uuid}")
async def update_video(
    user: Annotated[User, Depends(check_user)],
    uuid: UUID,
    content: UpdateVideoContent,
):
    if not user:
        return badresponse("Unauthorized", 401)
    video = await adapter.get_by_id(Video, uuid)
    if not video:
        return badresponse("Video not found", 404)
    if video.author_id != user.id:
        return badresponse("Forbidden", 403)
    await adapter.update_by_id(Video, uuid, {"description": content.description})
    return okresp()
