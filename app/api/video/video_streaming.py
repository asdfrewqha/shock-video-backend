import mimetypes
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
import requests

from app.core.config import SUPABASE_API
from app.core.dependencies import badresponse, check_user
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import User, Video, View


router = APIRouter()


@router.get("/stream-video/{uuid}")
async def stream_by_uuid(user: Annotated[User, Depends(check_user)], uuid: UUID, request: Request):
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
    if user:
        await adapter.insert(View, {"user_id": user.id, "video_id": uuid})
    views = media.views + 1
    await adapter.update_by_id(Video, uuid, {"views": views})

    response_headers = {
        "Content-Length": r.headers.get("Content-Length", ""),
        "Content-Range": r.headers.get("Content-Range", ""),
        "Accept-Ranges": r.headers.get(
            "Accept-Ranges",
            "bytes" if mime_type.startswith("video/") else "none",
        ),
    }

    return StreamingResponse(
        r.iter_content(chunk_size=8192),
        status_code=r.status_code,
        media_type=mime_type,
        headers={k: v for k, v in response_headers.items() if v},
    )
