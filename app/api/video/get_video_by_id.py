from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user
from app.models.auth_schemas import VideoResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Like, User, Video


router = APIRouter()


@router.get("/get-video-by-id/{uuid}", response_model=VideoResponse)
async def get_video_by_id(uuid: UUID, user: Annotated[User, Depends(check_user)]):
    video_db = await adapter.get_by_id(Video, uuid)
    if not video_db:
        return badresponse("Video not found", 404)
    author_db = await adapter.get_by_id(User, video_db.author_id)
    if user:
        user_id = user.id
        exsisting_like = await adapter.get_by_values(
            Like,
            {"user_id": user_id, "video_id": video_db.id},
        )
        if exsisting_like:
            like = exsisting_like[0].like
            liked = True if like is True else False
            disliked = True if like is False else False
        else:
            liked = False
            disliked = False
    else:
        liked = False
        disliked = False
    video_res = VideoResponse(
        id=uuid,
        sup_url=video_db.url,
        serv_url=f"https://api.vickz.ru/stream-video/{uuid}",
        author_id=video_db.author_id,
        author_name=author_db.name,
        author_username=author_db.username,
        is_liked_by_user=liked,
        is_disliked_by_user=disliked,
        views=video_db.views,
        likes=video_db.likes,
        dislikes=video_db.dislikes,
        comments=video_db.comments,
        description=video_db.description,
        created_at=video_db.created_at,
    )
    return video_res
