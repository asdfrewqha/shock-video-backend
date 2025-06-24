import logging
import os
import re
from urllib.parse import urlparse
from uuid import UUID

from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer
from supabase import create_client

from config import SUPABASE_API, SUPABASE_URL
from models.db_source.db_adapter import adapter
from models.schemas.auth_schemas import VideoRequest
from models.tables.db_tables import User, Video
from models.tokens.token_manager import TokenManager


router = APIRouter()
Bear = HTTPBearer(auto_error=False)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_file_suffix(url: str) -> str:
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lstrip(".")


def extract_uuid_from_url(url: str) -> str | None:
    match = re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}",
        url,
    )
    return match.group(0) if match else None


@router.delete("/delete-video")
async def delete_video(
        video: VideoRequest,
        access_token: str = Security(Bear)):
    if not access_token or not access_token.credentials:
        return JSONResponse(
            {"message": "Unauthorized", "status": "error"}, status_code=401
        )
    data = TokenManager.decode_token(access_token.credentials)
    supabase = create_client(SUPABASE_URL, SUPABASE_API)
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

    if "error" in data:
        return JSONResponse(
            content={
                "message": data["error"],
                "status": "error"},
            status_code=401)
    if data["type"] != "access":
        return JSONResponse(
            content={"message": "Invalid token type", "status": "error"},
            status_code=401,
        )

    user_db = adapter.get_by_id(User, UUID(data["sub"]))
    if not user_db:
        return JSONResponse(
            content={
                "message": "Invalid token",
                "status": "error"},
            status_code=401)
    video_result = adapter.get_by_value(Video, "id", id)
    if not video_result:
        return JSONResponse(
            content={
                "message": "There is no video with this id",
                "status": "error"},
            status_code=404,
        )
    video_db = video_result[0]
    if video_db.author_id != user_db.id:
        return JSONResponse(
            content={
                "message": "You're not author of this video",
                "status": "error"},
            status_code=403,
        )

    filepath = f"{user_db.username}/{id}.{get_file_suffix(video_db.url)}"
    supabase.storage.from_("videos").remove([filepath])
    logger.info(filepath)
    adapter.delete(Video, id)
    return Response(status_code=204)
