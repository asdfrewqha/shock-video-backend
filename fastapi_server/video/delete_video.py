import logging
import os
from typing import Annotated
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from supabase import create_client

from config import SUPABASE_API, SUPABASE_URL
from dependencies import check_user
from models.db_source.db_adapter import adapter
from models.tables.db_tables import User, Video


router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
supabase = create_client(SUPABASE_URL, SUPABASE_API)


def get_file_suffix(url: str) -> str:
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lstrip(".")


@router.delete("/delete-video/{uuid}", status_code=204)
async def delete_video(
        uuid: UUID,
        user: Annotated[User, Depends(check_user)]):
    if not user:
        return JSONResponse(
            content={
                "message": "Invalid token",
                "status": "error"},
            status_code=401)
    video_result = await adapter.get_by_id(Video, uuid)
    if not video_result:
        return JSONResponse(
            content={
                "message": "There is no video with this id",
                "status": "error"},
            status_code=404,
        )
    if video_result.author_id != user.id:
        return JSONResponse(
            content={
                "message": "You're not author of this video",
                "status": "error"},
            status_code=403,
        )

    filepath = f"{user.username}/{id}.{get_file_suffix(video_result.url)}"
    supabase.storage.from_("videos").remove([filepath])
    logger.info(filepath)
    await adapter.delete(Video, id)
    return Response(status_code=204)
