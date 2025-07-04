from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user
from app.models.auth_schemas import UserProfileResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Like, User


router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def profile(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    liked_videos_db = await adapter.get_by_values(Like, {"user_id": user.id, "like": True})
    liked_videos = []
    for like in liked_videos_db:
        liked_videos.append(str(like.video_id))
    disliked_videos_db = await adapter.get_by_values(Like, {"user_id": user.id, "like": False})
    disliked_videos = []
    for like in disliked_videos_db:
        disliked_videos.append(str(like.video_id))
    response_user = UserProfileResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        name=user.name,
        role=user.role,
        liked_videos=liked_videos,
        disliked_videos=disliked_videos,
        description=user.description,
        followers_count=user.followers_count,
        subscriptions_count=user.subscriptions_count,
    )

    return response_user
