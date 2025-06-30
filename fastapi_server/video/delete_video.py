import logging
import os
from typing import Annotated
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from supabase import create_client

from config import SUPABASE_API, SUPABASE_URL
from dependencies import check_user, badresponse
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
        return badresponse("Unauthorized", 401)
    video_result = await adapter.get_by_id(Video, uuid)
    if not video_result:
        return badresponse("Video not found", 404)
    if video_result.author_id != user.id:
        return badresponse("Forbidden", 403)

    filepath = f"{user.username}/{id}.{get_file_suffix(video_result.url)}"
    supabase.storage.from_("videos").remove([filepath])
    logger.info(filepath)
    await adapter.delete(Video, id)
    return Response(status_code=204)
