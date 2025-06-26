from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
import requests

from config import SUPABASE_API
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Video


router = APIRouter()


@router.get("/stream-video/{uuid}")
async def stream_by_uuid_sync(uuid: str, request: Request):
    video = await adapter.get_by_id(Video, uuid)
    if not video or not video.url:
        return JSONResponse(status_code=404, content={"detail": "Video not found"})

    headers = {
        "Authorization": f"Bearer {SUPABASE_API}",
        "Range": request.headers.get("range", None),
    }
    headers = {k: v for k, v in headers.items() if v is not None}

    r = requests.get(video.url, headers=headers, stream=True)

    if r.status_code not in (200, 206):
        return JSONResponse(status_code=r.status_code, content={"detail": "Video not accessible"})

    return StreamingResponse(
        r.iter_content(chunk_size=8192),
        status_code=r.status_code,
        media_type="video/mp4",
        headers={
            "Content-Length": r.headers.get("Content-Length", ""),
            "Accept-Ranges": "bytes",
            "Content-Range": r.headers.get("Content-Range", ""),
        },
    )
