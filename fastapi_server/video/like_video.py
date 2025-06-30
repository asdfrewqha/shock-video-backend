from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from dependencies import check_user
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
        return JSONResponse(
            content={
                "message": "Invalid user",
                "status": "error"},
            status_code=401)

    video = await adapter.get_by_id(Video, uuid)
    if not video:
        return JSONResponse(
            content={
                "message": "Video not found",
                "status": "error"},
            status_code=404)

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
            await adapter.update(
                Video,
                {"likes": video.likes, "dislikes": video.dislikes},
                uuid
            )
            return JSONResponse(
                content={
                    "message": f"Video un{'liked' if like else 'disliked'} successfully"
                }
            )

    await adapter.insert(Like,
                         {"user_id": user.id,
                          "video_id": uuid,
                          "like": like})

    if like:
        video.likes += 1
    else:
        video.dislikes += 1

    await adapter.update(Video, {"likes": video.likes,
                                 "dislikes": video.dislikes}, uuid)

    return JSONResponse(
        content={
            "message": f"Video {'liked' if like else 'disliked'} successfully"
        })
