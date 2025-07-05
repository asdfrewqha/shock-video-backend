from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends

from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment, User, Video


router = APIRouter()


@router.post("/add-comment/{video_id}")
async def add_comment(
    user: Annotated[User, Depends(check_user)],
    video_id: UUID,
    parent_id: UUID | None = None,
    content: str = Body(...),
):
    if not user:
        return badresponse("Unauthorized", 401)
    if len(content) < 2:
        return badresponse("Too short")
    video = await adapter.get_by_id(Video, video_id)
    if not video:
        return badresponse("Video not found", 404)
    parent_comment = await adapter.get_by_id(Comment, parent_id)
    if parent_comment:
        parent_username = parent_comment.user_username
    else:
        parent_username = None
    new_comment = {
        "user_id": user.id,
        "user_name": user.name,
        "user_username": user.username,
        "video_id": video_id,
        "parent_id": parent_id,
        "parent_username": parent_username,
        "content": content,
    }
    await adapter.update_by_id(Video, video_id, {"comments": video.comments + 1})
    new_comm = await adapter.insert(Comment, new_comment)
    return okresp(201, str(new_comm.id))
