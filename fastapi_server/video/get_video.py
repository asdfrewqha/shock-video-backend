from fastapi import APIRouter, Security
from fastapi.security import HTTPBearer
from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import VideoResponse
from models.tables.db_tables import Video
import random

router = APIRouter()

Bear = HTTPBearer(auto_error=False)


@router.get("/get-video", response_model=VideoResponse)
async def get_video(access_token: str = Security(Bear)):
    videos_db = adapter.get_all(Video)
    random_video = random.choice(videos_db)
    return {"url": random_video.url}
