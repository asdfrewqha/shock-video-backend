from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from dependencies import check_user
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Like, User


router = APIRouter()


@router.get("/get-likes-of-user")
async def get_likes(user: Annotated[User, Depends(check_user)]):
    if not user:
        return JSONResponse(
            {"message": "Invalid token", "status": "error"}, status_code=401
        )
    liked_videos_db = adapter.get_by_values(
        Like, {"user_id": user.id, "like": True})
    liked_videos = []
    for like in liked_videos_db:
        liked_videos.append(str(like.video_id))
    return JSONResponse({"liked_videos": liked_videos})


@router.get("/get-dislikes-of-user")
async def get_dislikes(user: Annotated[User, Depends(check_user)]):
    if not user:
        return JSONResponse(
            {"message": "Invalid token", "status": "error"}, status_code=401
        )
    disliked_videos_db = adapter.get_by_values(
        Like, {"user_id": user.id, "like": False}
    )
    disliked_videos = []
    for like in disliked_videos_db:
        disliked_videos.append(str(like.video_id))
    return JSONResponse({"disliked_videos": disliked_videos})
