from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import mimetypes

from config import SUPABASE_API
from models.db_source.db_adapter import adapter
from models.tables.db_tables import User

router = APIRouter()

@router.get("/get-profile-picture/{uuid}")
async def profile_picture(uuid: str, request: Request):
    user = await adapter.get_by_id(User, uuid)
    if not user.avatar_url:
        return JSONResponse(status_code=404, content={"detail": "Profile pic not found"})

    headers = {
        "Authorization": f"Bearer {SUPABASE_API}",
    }

    r = requests.get(user.avatar_url, headers=headers, stream=True)

    if r.status_code != 200:
        return JSONResponse(status_code=r.status_code, content={"detail": "Image not accessible"})

    return StreamingResponse(
        r.iter_content(chunk_size=8192),
        status_code=200,
        headers={
            "Content-Length": r.headers.get("Content-Length", ""),
        },
    )
