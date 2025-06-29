from fastapi import APIRouter
from fastapi.responses import JSONResponse

from fastapi_server.video.delete_video import extract_uuid_from_url
from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import Video
from models.tables.db_tables import VideoModel


router = APIRouter()


@router.post("/view-video")
async def view_video(video: VideoModel):
    if video.uuid:
        id = video.uuid
    elif video.url:
        id = extract_uuid_from_url(video.url)
        if not id:
            return JSONResponse(
                content={
                    "message": "Invalid request. Video not specified",
                    "status": "error",
                },
                status_code=400,
            )
    else:
        return JSONResponse(
            content={
                "message": "Invalid request. Video not specified",
                "status": "error",
            },
            status_code=400,
        )
    video_result = await adapter.get_by_value(Video, "id", id)
    if not video_result:
        return JSONResponse(
            content={
                "message": "There is no video with this id",
                "status": "error"},
            status_code=404,
        )
    video_db = video_result[0]
    views = video_db.views + 1
    await adapter.update(Video, {"views": views}, id)
    return JSONResponse(content={"message": "Views updated"})
