from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video
from fastapi_server.video.delete_video import extract_uuid_from_url

router = APIRouter()


@router.post("/view-video")
def view_video(uuid: str = Form(None), url: str = Form(None)):
    if uuid:
        id = uuid
    elif url:
        id = extract_uuid_from_url(url)
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
    video_result = adapter.get_by_value(Video, "id", id)
    if not video_result:
        return JSONResponse(
            content={"message": "There is no video with this id", "status": "error"},
            status_code=404,
        )
    video_db = video_result[0]
    views = video_db.views + 1
    adapter.update(Video, {"views": views}, id)
    return JSONResponse(content={"message": "Views updated"})
