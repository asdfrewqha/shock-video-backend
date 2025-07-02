import logging
from random import choice
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.core.dependencies import check_user
from app.models.auth_schemas import VideoResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Like, User, Video


router = APIRouter()

Bear = HTTPBearer(auto_error=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/get-video", response_model=VideoResponse)
async def get_video(user: Annotated[User, Depends(check_user)]):
    logger.info("Fetching all videos from DB...")
    videos_db = await adapter.get_all(Video)
    logger.info(f"Fetched {len(videos_db)} videos")
    random_video = choice(videos_db)
    author_db = await adapter.get_by_id(User, random_video.author_id)
    if user:
        user_id = user.id
        exsisting_like = await adapter.get_by_values(
            Like, {"user_id": user_id, "video_id": random_video.id}
        )
        if exsisting_like:
            if exsisting_like[0].like:
                liked = True
                disliked = False
            else:
                liked = False
                disliked = True
        else:
            liked = False
            disliked = False
    else:
        liked = False
        disliked = False
    return VideoResponse(
        id=random_video.id,
        sup_url=random_video.url,
        serv_url=f"https://api.vickz.ru/stream-video/{random_video.id}",
        author_id=random_video.author_id,
        author_name=author_db.name,
        author_username=author_db.username,
        is_liked_by_user=liked,
        is_disliked_by_user=disliked,
        views=random_video.views,
        likes=random_video.likes,
        dislikes=random_video.dislikes,
        comments=random_video.comments,
        description=random_video.description,
    )
