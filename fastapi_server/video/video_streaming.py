from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from dependencies import check_user, badresponse, okresp
import requests
import mimetypes
from typing import Annotated

from config import SUPABASE_API
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video, User

router = APIRouter()


@router.get("/stream-video/{uuid}")
async def stream_by_uuid(
    user: Annotated[User, check_user],
    uuid: str,
    request: Request):
    media = await adapter.get_by_id(Video, uuid)
    if not media or not media.url:
        return badresponse("Media not found", 404)

    mime_type, _ = mimetypes.guess_type(media.url)
    if not mime_type:
        mime_type = "application/octet-stream" 

    headers = {
        "Authorization": f"Bearer {SUPABASE_API}",
    }

    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    r = requests.get(media.url, headers=headers, stream=True)

    if r.status_code not in (200, 206):
        return badresponse("Media not accessible", r.status_code)
    
    views = media.views + 1

    await adapter.update_by_id(Video, uuid, {"views": views})

    response_headers = {
        "Content-Length": r.headers.get("Content-Length", ""),
        "Content-Range": r.headers.get("Content-Range", ""),
        "Accept-Ranges": r.headers.get("Accept-Ranges", "bytes" if mime_type.startswith("video/") else "none"),
    }

    return StreamingResponse(
        r.iter_content(chunk_size=8192),
        status_code=r.status_code,
        media_type=mime_type,
        headers={k: v for k, v in response_headers.items() if v},
    )
