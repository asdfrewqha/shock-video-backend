from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import badresponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Comment, Video


router = APIRouter()


@router.get("/get-comments/{video_id}")
async def get_comments(video_id: UUID):
    video = await adapter.get_by_id(Video, video_id)
    if not video:
        return badresponse("Video not found", 404)
    root_comments = await adapter.get_by_values(Comment, {"video_id": video_id, "parent_id": None})
    return root_comments
