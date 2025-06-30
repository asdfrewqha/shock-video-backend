from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video


router = APIRouter()


@router.post("/view-video/{uuid}")
async def view_video(uuid: UUID):
    video_result = await adapter.get_by_id(Video, uuid)
    if not video_result:
        return JSONResponse(
            content={
                "message": "There is no video with this id",
                "status": "error"},
            status_code=404,
        )
    views = video_result.views + 1
    await adapter.update(Video, {"views": views}, id)
    return JSONResponse(content={"message": "Views updated"})
