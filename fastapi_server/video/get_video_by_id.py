from uuid import UUID

from fastapi import APIRouter

from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import VideoResponse
from models.tables.db_tables import Video


router = APIRouter()


@router.get("/get-video-by-id", response_model=VideoResponse)
async def get_video_by_id(uuid: UUID):
    video_db = await adapter.get_by_id(Video, uuid)
    video_res = VideoResponse(
        id=uuid,
        url=video_db.url,
        author_id=video_db.author_id,
        views=video_db.views,
        likes=video_db.likes,
        dislikes=video_db.dislikes,
        description=video_db.description,
    )
    return video_res
