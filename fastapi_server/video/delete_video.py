from fastapi import APIRouter, Security, Form
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse, Response
from models.db_source.db_adapter import adapter
from models.tokens.token_manager import TokenManager
from supabase import create_client
from config import SUPABASE_API, SUPABASE_URL
from models.tables.db_tables import Video, User
from urllib.parse import urlparse
import logging
import os
import re

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
    uuid: str = Form(None), url: str = Form(None), access_token: str = Security(Bear)
):
    data = TokenManager.decode_token(access_token.credentials)
    supabase = create_client(SUPABASE_URL, SUPABASE_API)
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

    if "error" in data:
        return JSONResponse(
            content={"message": data["error"], "status": "error"}, status_code=401
        )
    if data["type"] != "access":
        return JSONResponse(
            content={"message": "Invalid token type", "status": "error"},
            status_code=401,
        )

    user_result = adapter.get_by_value(User, "username", data["username"])
    if not user_result:
        return JSONResponse(
            content={"message": "Invalid token", "status": "error"}, status_code=401
        )
    video_result = adapter.get_by_value(Video, "id", id)
    if not video_result:
        return JSONResponse(
            content={"message": "There is no video with this id", "status": "error"},
            status_code=404,
        )

    user_db = user_result[0]
    video_db = video_result[0]
    if video_db.author_id != user_db.id:
        return JSONResponse(
            content={"message": "You're not author of this video", "status": "error"},
            status_code=403,
        )

    filepath = f"{user_db.username}/{id}.{get_file_suffix(video_db.url)}"
    supabase.storage.from_("videos").remove([filepath])
    logger.info(filepath)
    adapter.delete(Video, id)
    return Response(status_code=204)
