from uuid import UUID

from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from models.db_source.db_adapter import adapter
from models.tables.db_tables import Like, User
from models.tokens.token_manager import TokenManager


router = APIRouter()
Bear = HTTPBearer(auto_error=False)


@router.get("/get-likes-of-user")
async def get_likes(access_token: str = Security(Bear)):
    if not access_token or not access_token.credentials:
        return JSONResponse(
            {"message": "Unauthorized", "status": "error"}, status_code=401
        )
    data = TokenManager.decode_token(access_token.credentials)
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
            {"message": "Invalid token", "status": "error"}, status_code=401
        )
    liked_videos_db = adapter.get_by_values(
        Like, {"user_id": user_db.id, "like": True})
    liked_videos = []
    for like in liked_videos_db:
        liked_videos.append(str(like.video_id))
    return JSONResponse({"liked_videos": liked_videos})


@router.get("/get-dislikes-of-user")
async def get_dislikes(access_token: str = Security(Bear)):
    if not access_token or not access_token.credentials:
        return JSONResponse(
            {"message": "Unauthorized", "status": "error"}, status_code=401
        )
    data = TokenManager.decode_token(access_token.credentials)
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
            {"message": "Invalid token", "status": "error"}, status_code=401
        )
    disliked_videos_db = adapter.get_by_values(
        Like, {"user_id": user_db.id, "like": False}
    )
    disliked_videos = []
    for like in disliked_videos_db:
        disliked_videos.append(str(like.video_id))
    return JSONResponse({"disliked_videos": disliked_videos})
