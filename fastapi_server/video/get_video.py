import logging
from random import choice

from fastapi import APIRouter, Security
from fastapi.security import HTTPBearer

from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import VideoResponse
from models.tables.db_tables import Video


router = APIRouter()

Bear = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/get-video", response_model=VideoResponse)
async def get_video(access_token: str = Security(Bear)):
    logger.info("Fetching all videos from DB...")
    videos_db = await adapter.get_all(Video)
    logger.info(f"Fetched {len(videos_db)} videos")
    random_video = choice(videos_db)
    return VideoResponse(
        id=random_video.id,
        sup_url=random_video.url,
        serv_url=f"https://api.vickz.ru/stream-video/{random_video.id}",
        author_id=random_video.author_id,
        views=random_video.views,
        likes=random_video.likes,
        dislikes=random_video.dislikes,
        description=random_video.description,
    )
