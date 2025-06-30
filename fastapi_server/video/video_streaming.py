from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import mimetypes

from config import SUPABASE_API
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video

router = APIRouter()


@router.get("/stream-video/{uuid}")
async def stream_by_uuid(uuid: str, request: Request):
    media = await adapter.get_by_id(Video, uuid)
    if not media or not media.url:
        return JSONResponse(status_code=404, content={"detail": "Media not found"})

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
        return JSONResponse(status_code=r.status_code, content={"detail": "Media not accessible"})

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
