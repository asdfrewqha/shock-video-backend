import logging
import os
from typing import Annotated
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase import create_client

from app.core.config import SUPABASE_API, SUPABASE_URL
from app.core.dependencies import badresponse, check_user, okresp
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User, Video


router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
supabase = create_client(SUPABASE_URL, SUPABASE_API)


def get_file_suffix(url: str) -> str:
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lstrip(".")


@router.delete("/delete-video/{uuid}", status_code=204)
async def delete_video(uuid: UUID, user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    video_result = await adapter.get_by_id(Video, uuid)
    if not video_result:
        return badresponse("Video not found", 404)
    if video_result.author_id != user.id:
        return badresponse("Forbidden", 403)

    filepath = f"{user.username}/{uuid}.{get_file_suffix(video_result.url)}"
    supabase.storage.from_("videos").remove([filepath])
    logger.info(filepath)
    await adapter.delete(Video, uuid)
    return okresp(204)
