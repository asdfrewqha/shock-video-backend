from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video

router = APIRouter()


@router.get("/get-videos-by-user-id")
async def get_videos_by_user_id(uuid: UUID):
    videos = adapter.get_by_value(Video, "author_id", uuid)
    ids = []
    for video in videos:
        ids.append(str(video.id))
    return JSONResponse({"video_ids": ids})
