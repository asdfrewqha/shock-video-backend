from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from dependencies import check_user, badresponse, okresp
from models.db_source.db_adapter import adapter
from models.tables.db_tables import Like, User, Video


router = APIRouter()


@router.post("/like-video")
async def like_video(
    uuid: UUID,
    user: Annotated[User, Depends(check_user)],
    like: bool = Query(True)
):
    if not user:
        return badresponse("Unauthorized", 401)
    video = await adapter.get_by_id(Video, uuid)
    if not video:
        return badresponse("Video not found", 404)

    existing_like = await adapter.get_by_values(
        Like, {"user_id": user.id, "video_id": uuid}
    )

    if existing_like:
        prev_like = existing_like[0]
        await adapter.delete(Like, prev_like.id)

        if prev_like.like:
            video.likes = max(video.likes - 1, 0)
        else:
            video.dislikes = max(video.dislikes - 1, 0)

        if prev_like.like == like:
            await adapter.update_by_id(
                Video,
                uuid,
                {"likes": video.likes, "dislikes": video.dislikes}
            )
            return okresp(message=f"{'liked' if like else 'disliked'}")

    await adapter.insert(Like,
                         {"user_id": user.id,
                          "video_id": uuid,
                          "like": like})

    if like:
        video.likes += 1
    else:
        video.dislikes += 1

    await adapter.update_by_id(Video, uuid, {"likes": video.likes,
                                 "dislikes": video.dislikes})

    return okresp(message=f"{'liked' if like else 'disliked'}")
