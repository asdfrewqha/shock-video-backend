from random import choice
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import badresponse, check_user
from app.models.auth_schemas import VideoResponse
from app.models.db_source.db_adapter import adapter
from app.models.db_source.db_tables import Like, Subscription, User, Video


router = APIRouter()


@router.get("/get-video-sub", response_model=VideoResponse)
async def get_video_sub(user: Annotated[User, Depends(check_user)]):
    if not user:
        return badresponse("Unauthorized", 401)
    subscriptions = await adapter.get_by_value(Subscription, "subscriber_id", user.id)
    sub_list = [sub.subscribed_to_id for sub in subscriptions]
    video_list = []
    for sub in sub_list:
        video = await adapter.get_by_value(Video, "author_id", sub)
        if video:
            video_list.append(video)
    if video_list:
        rand = choice(video_list)
        author = await adapter.get_by_id(User, rand.author_id)
        ex_like = await adapter.get_by_values(Like, {"user_id": user.id, "video_id": rand.id})
        if ex_like:
            like = ex_like[0].like
            liked = True if like is True else False
            disliked = True if like is False else False
        else:
            liked = False
            disliked = False
        return VideoResponse(
            id=rand.id,
            sup_url=rand.sup_url,
            serv_url=rand.serv_url,
            author_id=rand.author_id,
            author_name=author.name,
            author_username=author.username,
            is_liked_by_user=liked,
            is_disliked_by_user=disliked,
            views=rand.views,
            likes=rand.likes,
            dislikes=rand.dislikes,
            comments=rand.comments,
            description=rand.description,
        )
    else:
        return badresponse("Videos not found", 404)
