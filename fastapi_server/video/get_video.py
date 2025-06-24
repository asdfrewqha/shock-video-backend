from random import choice

from fastapi import APIRouter, Security
from fastapi.security import HTTPBearer

from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import VideoResponse
from models.tables.db_tables import Video


router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/get-video", response_model=VideoResponse)
async def get_video(access_token: str = Security(Bear)):
    videos_db = adapter.get_all(Video)
    random_video = choice(videos_db)
    return VideoResponse(
        id=random_video.id,
        url=random_video.url,
        author_id=random_video.author_id,
        views=random_video.views,
        likes=random_video.likes,
        dislikes=random_video.dislikes,
        description=random_video.description,
    )
